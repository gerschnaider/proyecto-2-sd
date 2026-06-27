import asyncio
import websockets
import json
import logging
import os
import psycopg2
import aio_pika

logging.basicConfig(level=logging.INFO)

# Configuración de entorno
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "noticias_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgrespassword")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")

# Diccionario global para websockets
# Formato: { category_id: set(websocket1, websocket2, ...) }
suscriptores = {}

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
    )

def verificar_suscripcion_db(user_id, category_id):
    """Consulta bloqueante a la Base de Datos. Verifica si el usuario está suscripto."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM subscriptions WHERE user_id = %s AND category_id = %s;",
            (user_id, category_id)
        )
        existe = cur.fetchone() is not None
        cur.close()
        conn.close()
        return existe
    except Exception as e:
        logging.error(f"Error verificando suscripción en BD: {e}")
        return False

async def websocket_handler(websocket):
    """Maneja las conexiones entrantes de los clientes."""
    try:
        # 1. Esperamos el mensaje de autenticación/suscripción
        mensaje = await websocket.recv()
        datos = json.loads(mensaje)
        user_id = datos.get("user_id")
        category_id = datos.get("category_id")
        
        if not user_id or not category_id:
            await websocket.send(json.dumps({"error": "Faltan user_id o category_id"}))
            return
            
        # 2. Verificar en PostgreSQL si el usuario tiene permiso (de forma asíncrona)
        esta_suscripto = await asyncio.to_thread(verificar_suscripcion_db, user_id, category_id)
        
        if not esta_suscripto:
            logging.warning(f"Usuario {user_id} intentó escuchar categoría {category_id} sin permiso en la BD.")
            await websocket.send(json.dumps({"error": "No estás suscripto a esta categoría en la Base de Datos."}))
            return
            
        # 3. Registrar el websocket en memoria local
        if category_id not in suscriptores:
            suscriptores[category_id] = set()
        suscriptores[category_id].add(websocket)
        logging.info(f"Usuario {user_id} validado y conectado a la categoría {category_id}")
        
        await websocket.send(json.dumps({"mensaje": f"Conectado a la categoría {category_id} con éxito. Esperando noticias..."}))
        
        # 4. Mantener viva la conexión
        async for _ in websocket:
            pass 
            
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        logging.error(f"Error inesperado en WS: {e}")
    finally:
        # Limpieza
        for cat, wss in list(suscriptores.items()):
            if websocket in wss:
                wss.remove(websocket)

async def procesar_mensaje_rabbitmq(message: aio_pika.abc.AbstractIncomingMessage):
    """Se ejecuta cada vez que Sabrina tira un JSON en RabbitMQ."""
    async with message.process():
        cuerpo = message.body.decode()
        logging.info(f"JSON recibido de RabbitMQ: {cuerpo}")
        
        try:
            noticia = json.loads(cuerpo)
            category_id = noticia.get("id_categoria")
        except json.JSONDecodeError:
            logging.error("El mensaje de RabbitMQ no es un JSON válido.")
            return

        if not category_id:
            logging.error("El JSON de la noticia no tiene 'id_categoria'.")
            return
        
        # Enrutamiento Inteligente (Sin tocar la BD):
        # Repartir a los WebSockets conectados que pidieron esta categoría
        if category_id in suscriptores and suscriptores[category_id]:
            mensaje_json = json.dumps(noticia)
            for ws in suscriptores[category_id]:
                try:
                    await ws.send(mensaje_json)
                except Exception as e:
                    logging.error(f"Error enviando JSON al WS del cliente: {e}")

async def rabbitmq_listener():
    """Conecta a RabbitMQ y se suscribe al canal global de Sabri."""
    await asyncio.sleep(5) 
    try:
        connection = await aio_pika.connect_robust(f"amqp://guest:guest@{RABBITMQ_HOST}/")
        channel = await connection.channel()
        
        # Mismo exchange 'fanout' que usa Sabrina
        exchange = await channel.declare_exchange('noticias_exchange', aio_pika.ExchangeType.FANOUT)
        
        # Cola exclusiva de esta réplica
        queue = await channel.declare_queue('', exclusive=True)
        await queue.bind(exchange)
        
        logging.info(f"Conectado a RabbitMQ en {RABBITMQ_HOST}. Escuchando noticias en vivo...")
        
        await queue.consume(procesar_mensaje_rabbitmq)
        await asyncio.Future() 
    except Exception as e:
        logging.error(f"Error fatal conectando a RabbitMQ: {e}")

async def main():
    logging.info("Iniciando servicio de distribución de noticias (Optimizadísimo)...")
    ws_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)
    
    await asyncio.gather(
        ws_server,
        rabbitmq_listener()
    )

if __name__ == "__main__":
    asyncio.run(main())
