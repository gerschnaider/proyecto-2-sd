# Comandos para el Servicio de Envío de Noticias (send-news)

Estos son los comandos e indicaciones para interactuar con el microservicio `send-news`.

> **Nota importante:** Este servicio utiliza **WebSocket** (no HTTP REST), por lo que `curl` convencional **no funciona** para conectarse. Se debe usar el **script cliente Python** incluido o una herramienta como `websocat`.

---

## Requisitos previos

1. El servicio `send-news` debe estar levantado (puerto **8765** por defecto).
2. RabbitMQ debe estar corriendo (el servicio lo necesita para recibir noticias).
3. La base de datos PostgreSQL debe estar activa.
4. El usuario que se conecta **debe existir** en la tabla `users` y **debe estar suscripto** a la categoría deseada en la tabla `subscriptions` (usar el servicio `new-subscriptions` para eso).

---

## Opción 1: Usar el cliente Python incluido (`client_suscriptor.py`)

Este es el método recomendado. El script se conecta al WebSocket, envía las credenciales de suscripción, y queda escuchando noticias en tiempo real.

### Pasos

1. Instalar la dependencia:
```bash
pip install websockets
```

2. Editar `user_id` y `category_id` en el archivo `client_suscriptor.py` (líneas 50-51) o ejecutarlo directamente con los valores por defecto:
```bash
python client_suscriptor.py
```

### Ejemplo de salida esperada
```
Conectado a ws://localhost:8765
[SERVIDOR] Conectado a la categoría 2 con éxito. Esperando noticias...

==================================================
NUEVA NOTICIA DE CATEGORÍA 2
TÍTULO: Economía en alza
--------------------------------------------------
El mercado subió un 5% hoy...
==================================================
```

### Conectarse a un nodo remoto (Swarm)
Si el servicio está en otra máquina, editar la línea 6 del script:
```python
uri = "ws://<ip_del_nodo>:8765"
```

---

## Opción 2: Usar `websocat` (alternativa de línea de comandos)

`websocat` es el equivalente a `curl` pero para WebSockets. Se puede instalar desde: https://github.com/vi/websocat

### Conectarse y suscribirse a una categoría

```bash
echo '{"user_id": <id_del_usuario>, "category_id": <id_del_area>}' | websocat ws://<ip>:8765
```

*Ejemplo:*
```bash
echo '{"user_id": 1, "category_id": 2}' | websocat ws://localhost:8765
```

### Quedarse escuchando noticias en vivo (modo interactivo)

```bash
websocat ws://<ip>:8765
```
Luego escribir manualmente el JSON de autenticación y presionar Enter:
```json
{"user_id": 1, "category_id": 2}
```
La terminal quedará abierta esperando noticias en tiempo real. Presionar `Ctrl+C` para salir.

---

## Protocolo WebSocket - Referencia Rápida

### Mensaje de conexión (cliente → servidor)
Al conectarse, el cliente **debe enviar** un JSON con su `user_id` y `category_id`:
```json
{"user_id": 1, "category_id": 2}
```

### Respuestas posibles del servidor

| Situación | Respuesta del servidor |
|---|---|
| Conexión exitosa | `{"mensaje": "Conectado a la categoría 2 con éxito. Esperando noticias..."}` |
| Faltan campos | `{"error": "Faltan user_id o category_id"}` |
| No está suscripto en la BD | `{"error": "No estás suscripto a esta categoría en la Base de Datos."}` |
| Noticia nueva | `{"id_categoria": 2, "titulo": "...", "texto": "..."}` |

### Flujo de comunicación
```
Cliente                          Servidor (send-news)
  |                                    |
  |--- Conectar WebSocket ------------>|
  |--- {"user_id":1,"category_id":2}-->|
  |                                    |--- Verifica en PostgreSQL
  |<-- {"mensaje":"Conectado..."}------|
  |                                    |
  |    (RabbitMQ publica una noticia)  |
  |<-- {"titulo":"...","texto":"..."} -|
  |<-- {"titulo":"...","texto":"..."} -|
  |        ...                         |
```

---

## Prueba End-to-End (Flujo Completo)

Esta es la prueba más importante: verificar que una noticia publicada llega al cliente suscripto.

### Paso 1: Abrir una terminal y conectar un cliente
```bash
python client_suscriptor.py
```
El cliente se quedará escuchando noticias en la categoría configurada.

### Paso 2: En OTRA terminal, publicar una noticia via `servicio_recepcion`
```bash
curl -X POST http://<ip>:50050/api/noticias \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Noticia de prueba", "id_autor": 2, "id_categoria": 2, "texto": "Contenido de la noticia."}'
```

### Paso 3: Verificar
En la primera terminal debería aparecer la noticia automáticamente. Si llega, el servicio funciona correctamente.

### Alternativa: Publicar directo a RabbitMQ (sin servicio_recepcion)
Si el `servicio_recepcion` no está disponible, se puede publicar directo a RabbitMQ con Python:
```bash
python -c "
import pika, json
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
ch = conn.channel()
ch.exchange_declare(exchange='noticias_exchange', exchange_type='fanout')
ch.basic_publish(exchange='noticias_exchange', routing_key='', body=json.dumps({
    'news_id': 9999, 'titulo': 'Noticia de prueba', 'id_autor': 2, 'id_categoria': 2, 'texto': 'Texto de la noticia.'
}))
conn.close()
print('Noticia publicada en RabbitMQ')
"
```
> **Requisito:** `pip install pika`

---

## ¿Por qué no se puede usar `curl`?

`curl` trabaja con HTTP (request → response). Este servicio usa **WebSocket**, que es una conexión persistente bidireccional. Por eso se necesita `websocat` o un cliente WebSocket como el script Python.
