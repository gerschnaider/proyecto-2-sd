
#!/bin/bash

# Podés cambiar el puerto a 8081 o 8082 si querés probar el balanceo de réplicas
API_URL="http://localhost:8080/areas"

echo "================================================="
echo "   INICIANDO TEST DEL MICROSERVICIO DE ÁREAS     "
echo "================================================="

# ---------------------------------------------------------
# PRUEBA 1: Crear primera área
# ---------------------------------------------------------
echo -e "\n[TEST 1] Creando área 'Sistemas Embebidos'..."
# Guardamos la respuesta del curl en una variable (-s silencia el output extra de curl)
RES1=$(curl -s -X POST $API_URL -H "Content-Type: application/json" -d '{"name": "Sistemas Embebidos", "user_id": 1}')
echo "-> Respuesta del servidor: $RES1"


# ---------------------------------------------------------
# PRUEBA 2: Crear segunda área
# ---------------------------------------------------------
echo -e "\n[TEST 2] Creando área 'Práctica Profesional Supervisada'..."
RES2=$(curl -s -X POST $API_URL -H "Content-Type: application/json" -d '{"name": "Práctica Profesional Supervisada", "user_id": 1}')
echo "-> Respuesta del servidor: $RES2"


# ---------------------------------------------------------
# PRUEBA 3: Forzar el error de nombre duplicado (HTTP 409)
# ---------------------------------------------------------
echo -e "\n[TEST 3] Intentando crear 'Sistemas Embebidos' de nuevo (Debería fallar)..."
# Usamos -w para imprimir también el código de estado HTTP final
curl -s -w "\n-> Código HTTP devuelto: %{http_code}\n" -X POST $API_URL -H "Content-Type: application/json" -d '{"name": "Sistemas Embebidos", "user_id": 1}'


# ---------------------------------------------------------
# PRUEBA 4: Intentar borrar con un impostor (HTTP 403)
# ---------------------------------------------------------
echo -e "\n\n[TEST 4] Intentando borrar 'Sistemas Embebidos' con el usuario 2 (Debería dar 403 Forbidden)..."
# Pasamos user_id: 2 en el body para simular que otro usuario intenta borrarla
curl -s -w "\n-> Código HTTP devuelto: %{http_code}\n" -X DELETE "$API_URL/Sistemas%20Embebidos" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 2}'


# ---------------------------------------------------------
# PRUEBA 5: Borrar las áreas creadas (Flujo feliz - HTTP 200)
# ---------------------------------------------------------
echo -e "\n\n[TEST 5] Limpiando la base de datos (Dueño correcto)..."

echo "Borrando 'Sistemas Embebidos'..."
# Ahora sí usamos el user_id: 1, que es el verdadero dueño
curl -s -X DELETE "$API_URL/Sistemas%20Embebidos" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1}'
echo ""

echo -e "\nBorrando 'Práctica Profesional Supervisada'..."
curl -s -X DELETE "$API_URL/Pr%C3%A1ctica%20Profesional%20Supervisada" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1}'
echo ""

echo -e "\n================================================="
echo "                 TEST FINALIZADO                 "
echo "================================================="