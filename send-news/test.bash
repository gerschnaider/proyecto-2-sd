#!/bin/bash

# =====================================================
# Script de prueba para el servicio send-news
# Prueba conexiones WebSocket y entrega de noticias
# =====================================================
# Requisitos: pip install websockets pika

WS_HOST="${1:-localhost}"
WS_PORT="${2:-8765}"
RABBITMQ_HOST="${3:-localhost}"

echo ""
echo "====================================="
echo "  PRUEBAS DEL SERVICIO SEND-NEWS"
echo "  WebSocket: ws://${WS_HOST}:${WS_PORT}"
echo "  RabbitMQ:  ${RABBITMQ_HOST}"
echo "====================================="
echo ""

# --------------------------------------------------
# Test 1: Conexión válida (usuario suscripto)
# --------------------------------------------------
echo "====================================="
echo "1. Conexión válida (user_id=1, category_id=2)"
echo "====================================="
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://${WS_HOST}:${WS_PORT}') as ws:
        await ws.send(json.dumps({'user_id': 1, 'category_id': 2}))
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        datos = json.loads(msg)
        if 'mensaje' in datos:
            print(f'✅ ÉXITO: {datos[\"mensaje\"]}')
        else:
            print(f'❌ ERROR: {datos}')
asyncio.run(test())
" 2>&1 || echo "❌ No se pudo conectar al WebSocket"
echo ""

# --------------------------------------------------
# Test 2: Conexión sin campos requeridos
# --------------------------------------------------
echo "====================================="
echo "2. Conexión sin campos (debe dar error)"
echo "====================================="
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://${WS_HOST}:${WS_PORT}') as ws:
        await ws.send(json.dumps({}))
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        datos = json.loads(msg)
        if 'error' in datos:
            print(f'✅ Error esperado: {datos[\"error\"]}')
        else:
            print(f'⚠️  Respuesta inesperada: {datos}')
asyncio.run(test())
" 2>&1 || echo "❌ No se pudo conectar al WebSocket"
echo ""

# --------------------------------------------------
# Test 3: Usuario no suscripto a la categoría
# --------------------------------------------------
echo "====================================="
echo "3. Usuario no suscripto (user_id=10, category_id=1)"
echo "====================================="
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://${WS_HOST}:${WS_PORT}') as ws:
        await ws.send(json.dumps({'user_id': 10, 'category_id': 1}))
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        datos = json.loads(msg)
        if 'error' in datos:
            print(f'✅ Error esperado: {datos[\"error\"]}')
        else:
            print(f'⚠️  Respuesta inesperada: {datos}')
asyncio.run(test())
" 2>&1 || echo "❌ No se pudo conectar al WebSocket"
echo ""

# --------------------------------------------------
# Test 4: Usuario inexistente
# --------------------------------------------------
echo "====================================="
echo "4. Usuario inexistente (user_id=999, category_id=1)"
echo "====================================="
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://${WS_HOST}:${WS_PORT}') as ws:
        await ws.send(json.dumps({'user_id': 999, 'category_id': 1}))
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        datos = json.loads(msg)
        if 'error' in datos:
            print(f'✅ Error esperado: {datos[\"error\"]}')
        else:
            print(f'⚠️  Respuesta inesperada: {datos}')
asyncio.run(test())
" 2>&1 || echo "❌ No se pudo conectar al WebSocket"
echo ""

# --------------------------------------------------
# Test 5: PRUEBA END-TO-END (La más importante)
# Conectar un cliente WS + publicar en RabbitMQ
# + verificar que la noticia llega al cliente
# --------------------------------------------------
echo "====================================="
echo "5. 🔥 PRUEBA END-TO-END: Entrega de noticias"
echo "   (Conectar WS + Publicar en RabbitMQ + Recibir)"
echo "====================================="
python3 -c "
import asyncio, websockets, json, threading, time

resultado = {}

async def cliente_ws():
    async with websockets.connect('ws://${WS_HOST}:${WS_PORT}') as ws:
        await ws.send(json.dumps({'user_id': 1, 'category_id': 2}))
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        datos = json.loads(msg)
        if 'error' in datos:
            print(f'❌ No se pudo conectar: {datos[\"error\"]}')
            return
        print(f'📡 Cliente conectado: {datos[\"mensaje\"]}')
        print('⏳ Esperando noticia...')
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=15)
            datos = json.loads(msg)
            resultado.update(datos)
            print(f'🎉 ¡NOTICIA RECIBIDA!')
            print(f'   Título:    {datos.get(\"titulo\", \"?\")}')
            print(f'   Categoría: {datos.get(\"id_categoria\", \"?\")}')
            print(f'   Texto:     {datos.get(\"texto\", \"?\")}')
        except asyncio.TimeoutError:
            print('❌ Timeout: La noticia no llegó en 15 segundos')

def publicar():
    time.sleep(3)
    import pika
    conn = pika.BlockingConnection(pika.ConnectionParameters('${RABBITMQ_HOST}'))
    ch = conn.channel()
    ch.exchange_declare(exchange='noticias_exchange', exchange_type='fanout')
    noticia = {'news_id': 9999, 'titulo': 'Test E2E - Noticia de prueba', 'id_autor': 2, 'id_categoria': 2, 'texto': 'Si llego aca, el servicio funciona.'}
    ch.basic_publish(exchange='noticias_exchange', routing_key='', body=json.dumps(noticia))
    print(f'📤 Noticia publicada en RabbitMQ')
    conn.close()

threading.Thread(target=publicar, daemon=True).start()
asyncio.run(cliente_ws())

if resultado:
    print('✅ TEST E2E: PASÓ')
else:
    print('❌ TEST E2E: FALLÓ')
" 2>&1 || echo "❌ Error ejecutando el test E2E (¿está instalado pika?)"
echo ""

echo "====================================="
echo "Fin de las pruebas"
echo "====================================="
