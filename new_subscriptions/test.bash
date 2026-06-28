#!/bin/bash

URL="http://127.0.0.1:8000"

echo "====================================="
echo "1. Suscripción válida (10 -> Área 8)"
echo "====================================="
curl -s -X POST "$URL/suscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":10,"category_id":8}'
echo -e "\n"

echo "====================================="
echo "2. Suscripción duplicada (1 -> Área 1)"
echo "====================================="
curl -s -X POST "$URL/suscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"category_id":1}'
echo -e "\n"

echo "====================================="
echo "3. Área inexistente"
echo "====================================="
curl -s -X POST "$URL/suscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"category_id":99}'
echo -e "\n"

echo "====================================="
echo "4. Usuario inexistente"
echo "====================================="
curl -s -X POST "$URL/suscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":99,"category_id":1}'
echo -e "\n"

echo "====================================="
echo "5. Desuscripción válida (3 -> Área 4)"
echo "====================================="
curl -s -X DELETE "$URL/desuscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":3,"category_id":4}'
echo -e "\n"

echo "====================================="
echo "6. Desuscripción sin suscripción"
echo "====================================="
curl -s -X DELETE "$URL/desuscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":10,"category_id":2}'
echo -e "\n"

echo "====================================="
echo "7. Desuscripción de área inexistente"
echo "====================================="
curl -s -X DELETE "$URL/desuscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"category_id":99}'
echo -e "\n"

echo "====================================="
echo "8. Desuscripción de usuario inexistente"
echo "====================================="
curl -s -X DELETE "$URL/desuscribir" \
  -H "Content-Type: application/json" \
  -d '{"user_id":99,"category_id":1}'
echo -e "\n"

echo "====================================="
echo "Fin de las pruebas"
echo "====================================="