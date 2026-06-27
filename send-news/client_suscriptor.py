import asyncio
import websockets
import json

async def suscribir_y_escuchar(user_id, category_id):
    uri = "ws://localhost:8765"
    
    try:
        # 1. Nos conectamos al servidor WebSocket
        async with websockets.connect(uri) as websocket:
            print(f"Conectado a {uri}")
            
            # 2. Armamos el paquete de suscripción en formato JSON
            suscripcion = {
                "user_id": user_id,
                "category_id": category_id
            }
            
            # 3. Enviamos el JSON al conectarnos para autenticarnos
            await websocket.send(json.dumps(suscripcion))
            
            # 4. Bucle infinito escuchando los mensajes que empuja el servidor
            async for mensaje in websocket:
                datos = json.loads(mensaje)
                
                # Chequear si es un mensaje de error o conexión
                if "error" in datos:
                    print(f"[ERROR] {datos['error']}")
                    break
                if "mensaje" in datos:
                    print(f"[SERVIDOR] {datos['mensaje']}")
                    continue
                
                # Si llega acá, es una noticia real
                print("\n" + "="*50)
                print(f"NUEVA NOTICIA DE CATEGORÍA {category_id}")
                print(f"TÍTULO: {datos.get('titulo', 'Sin título')}")
                print("-" * 50)
                print(f"{datos.get('texto', '')}")
                print("="*50 + "\n")
                
    except websockets.exceptions.ConnectionClosed:
        print("El servidor cerró la conexión TCP.")
    except ConnectionRefusedError:
        print("Error: No se pudo conectar al servidor. ¿Está encendido el WebSocket en el puerto 8765?")

if __name__ == '__main__':
    # ATENCIÓN: Este usuario debe existir en la tabla `users` y 
    # debe estar suscripto a esta categoría en la tabla `subscriptions`.
    user_id_prueba = 1 
    category_id_a_escuchar = 2
    
    # Arrancamos el cliente asíncrono
    try:
        asyncio.run(suscribir_y_escuchar(user_id_prueba, category_id_a_escuchar))
    except KeyboardInterrupt:
        print("Saliendo...")
