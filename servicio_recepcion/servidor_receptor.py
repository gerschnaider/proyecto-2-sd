from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import uvicorn
import os
import pika
import json

app = FastAPI(title="Microservicio de Recepción", description="API Gateway para clientes que cargan noticias", version="1.0")

class NuevaNoticia(BaseModel):
    titulo: str
    id_autor: int
    id_categoria: int
    texto: str

# Creamos el endpoint
@app.post("/api/noticias")
def recibir_noticia(noticia: NuevaNoticia):
    print(f"Recibiendo nueva noticia: {noticia.titulo}")
    
    try:
        conexion = psycopg2.connect(
            host="db", 
            database="noticias_db",
            user="postgres",
            password="admin"
        )
        cursor = conexion.cursor()

        consulta_area = "SELECT is_deleted FROM areas WHERE category_id = %s;"
        cursor.execute(consulta_area, (noticia.id_categoria,))
        resultado_area = cursor.fetchone()

        # Si el área no existe en la tabla 'areas'
        if not resultado_area:
            cursor.close()
            conexion.close()
            raise HTTPException(status_code=404, detail="El área especificada no existe.")

        # Si el área existe, pero está borrada lógicamente (is_deleted == True)
        if resultado_area[0] is True:
            cursor.close()
            conexion.close()
            raise HTTPException(status_code=400, detail="El área está inactiva o eliminada. No se pueden publicar noticias aquí.")

        consulta_sql = """
            INSERT INTO news (title, user_id, category_id, content)
            VALUES (%s, %s, %s, %s)
            RETURNING news_id; 
        """
        
        cursor.execute(consulta_sql, (noticia.titulo, noticia.id_autor, noticia.id_categoria, noticia.texto))
        nuevo_id = cursor.fetchone()[0]

        conexion.commit()
        cursor.close()
        conexion.close()
        
        print(f"[ÉXITO DB] Noticia guardada en la base de datos con ID: {nuevo_id}")
        
        print("Avisando al servicio de distribución de noticias vía RabbitMQ...")
        try:
            rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            
            channel.exchange_declare(exchange='noticias_exchange', exchange_type='fanout')
            
            # Armamos el payload completo con los datos de la noticia
            mensaje_dict = {
                "news_id": nuevo_id,
                "titulo": noticia.titulo,
                "id_autor": noticia.id_autor,
                "id_categoria": noticia.id_categoria,
                "texto": noticia.texto
            }
            mensaje = json.dumps(mensaje_dict)
            
            channel.basic_publish(exchange='noticias_exchange', routing_key='', body=mensaje)
            
            print(f"[ÉXITO DISTRIBUCIÓN] Noticia ID {nuevo_id} (JSON) publicada en RabbitMQ")
            connection.close()
                
        except Exception as error_distribucion:
            print(f"[AVISO] La noticia se guardó, pero falló la distribución: {error_distribucion}")

        # Le respondemos al cliente
        return {
            "exito": True, 
            "mensaje": "Noticia recibida y procesada correctamente",
            "id_generado": nuevo_id
        }

    # Atrapamos los errores de FastAPI generados arriba (404 o 400) para no taparlos con un 500
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR GENERAL] {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# El motor que enciende el servidor
if __name__ == '__main__':
    print("Iniciando API Gateway en el puerto 50050...")
    uvicorn.run(app, host="0.0.0.0", port=50050)