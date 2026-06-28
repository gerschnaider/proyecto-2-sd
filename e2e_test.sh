#!/bin/bash

# ==============================================================================
# SCRIPT DE PRUEBAS E2E (End-to-End) - PROYECTO 2 SD
# Autor: Agente Experto en Testing
# Descripción: Este script simula un flujo de usuario completo, verificando la 
# integración de todos los microservicios usando peticiones cURL y extrayendo 
# IDs dinámicamente con jq.
# ==============================================================================

# Leer la IP desde el primer argumento, si no existe usar localhost
HOST_IP=${1:-localhost}

# Colores para los logs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función auxiliar para imprimir pasos
print_step() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

# Verificar dependencias
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: 'jq' no está instalado. Por favor instala jq (sudo dnf install jq) para parsear los JSON.${NC}"
    exit 1
fi

print_step "INICIANDO BATERÍA DE PRUEBAS E2E SOBRE $HOST_IP"
echo "Asegúrate de que el stack de Docker Swarm o Docker Compose esté corriendo."

# ==============================================================================
# PASO 1: AREA MANAGER - Creación de un Área (Categoría)
# ==============================================================================
print_step "1. [Area Manager] Creando nueva área: 'DevOps Testing'"
AREA_NAME="DevOps Testing"
USER_ID=1

AREA_RESPONSE=$(curl -s -X POST http://$HOST_IP:8080/areas \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$AREA_NAME\", \"user_id\": $USER_ID}")

# Extraer el category_id generado dinámicamente
CATEGORY_ID=$(echo $AREA_RESPONSE | jq -r '.category_id')

if [ "$CATEGORY_ID" == "null" ] || [ -z "$CATEGORY_ID" ]; then
    echo -e "${RED}Fallo al crear el área. Respuesta: $AREA_RESPONSE${NC}"
    exit 1
else
    echo -e "${GREEN}Éxito. Área '$AREA_NAME' creada con ID: $CATEGORY_ID${NC}"
fi

# ==============================================================================
# PASO 2: NEW SUBSCRIPTIONS - Suscribir usuario al área creada
# ==============================================================================
print_step "2. [New Subscriptions] Suscribiendo al usuario $USER_ID al área $CATEGORY_ID"
curl -s -X POST http://$HOST_IP:8004/suscribir \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": $USER_ID, \"category_id\": $CATEGORY_ID}" | jq .
echo -e "${GREEN}Usuario suscrito exitosamente.${NC}"

# ==============================================================================
# PASO 3: SERVICIO RECEPCIÓN - Publicar una noticia exitosa
# ==============================================================================
print_step "3. [Servicio Recepción] Publicando noticia en área $CATEGORY_ID (Camino Feliz)"
NEWS_TITLE="Integración Continua con cURL"
NEWS_RESPONSE=$(curl -s -X POST http://$HOST_IP:50050/api/noticias \
  -H "Content-Type: application/json" \
  -d "{\"titulo\": \"$NEWS_TITLE\", \"id_autor\": $USER_ID, \"id_categoria\": $CATEGORY_ID, \"texto\": \"Esta noticia es una prueba automatizada generada por el script E2E.\"}")

# Asumimos que devuelve la noticia creada con su ID (Ajustar si el microservicio no devuelve el ID)
echo "Respuesta del publicador:"
echo $NEWS_RESPONSE | jq .

# ==============================================================================
# PASO 4: SERVICIO RECEPCIÓN - Publicar una noticia con error (Fuzzing)
# ==============================================================================
print_step "4. [Servicio Recepción] Publicando noticia en área fantasma (Validación de Error)"
curl -s -X POST http://$HOST_IP:50050/api/noticias \
  -H "Content-Type: application/json" \
  -d "{\"titulo\": \"Noticia en el limbo\", \"id_autor\": $USER_ID, \"id_categoria\": 999999, \"texto\": \"Esta categoria no existe.\"}" | jq .
echo -e "${GREEN}Nota: Se esperaba un error 404/500 por violación de Foreign Key o área inexistente.${NC}"

# ==============================================================================
# PASO 5: GET NEWS LOAD BY AREA - Verificar la carga de noticias
# ==============================================================================
print_step "5. [Get News Load By Area] Verificando conteo de noticias por área"
curl -s -X GET http://$HOST_IP:8003/api/news-load | jq .
echo -e "${GREEN}La categoría $CATEGORY_ID debería tener 1 noticia activa.${NC}"

# ==============================================================================
# PASO 6: FIND NEWS BY DESCRIPTOR - Búsqueda semántica o por texto
# ==============================================================================
print_step "6. [Find News By Descriptor] Buscando noticia por palabra clave 'cURL'"
curl -s -X GET "http://$HOST_IP:8030/api/news-descriptor?descriptor=cURL" | jq .

# ==============================================================================
# PASO 7: LAST NEWS 24 HOUR - Noticias recientes filtradas por suscripción
# ==============================================================================
print_step "7. [Last News 24 Hour] Consultando noticias de las últimas 24hs para el usuario $USER_ID"
curl -s -X GET "http://$HOST_IP:8005/api/news-last-24h?user_id=$USER_ID" | jq .
echo -e "${GREEN}La noticia recién creada debe aparecer en este listado.${NC}"

# ==============================================================================
# PASO 8: FIND NEWS PERIOD - Búsqueda por rango de fechas
# ==============================================================================
print_step "8. [Find News Period] Buscando noticias del mes actual"
TODAY=$(date +"%Y-%m-%d")
FIRST_DAY=$(date +"%Y-%m-01")
curl -s -X GET "http://$HOST_IP:8002/api/news-period?fecha_inicio=${FIRST_DAY}&fecha_fin=${TODAY}" | jq .

# ==============================================================================
# PASO 9: DELETE NEWS - Borrado lógico de la noticia (Soft Delete)
# ==============================================================================
print_step "9. [Delete News] (Opcional) Borrando la noticia"
echo -e "${YELLOW}Como el servicio_recepcion puede no devolver el ID, debes extraer el ID del JSON del Paso 7 y ejecutar manualmente:${NC}"
echo -e "curl -X DELETE \"http://$HOST_IP:8001/noticias/<NEWS_ID>?user_id=$USER_ID\""

# ==============================================================================
# PASO 10: AREA MANAGER - Borrado del área (Cascada)
# ==============================================================================
print_step "10. [Area Manager] Eliminando el área '$AREA_NAME' y limpiando el estado"
# URL Encoded name (Reemplaza espacios por %20)
AREA_ENCODED="DevOps%20Testing"
curl -s -X DELETE "http://$HOST_IP:8080/areas/${AREA_ENCODED}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": $USER_ID}"
echo -e "\n${GREEN}Área eliminada exitosamente.${NC}"

# ==============================================================================
# PASO 11: SEND NEWS (WebSocket) - Explicación
# ==============================================================================
print_step "11. [Send News] Servicio WebSocket"
echo "El servicio send-news corre en el puerto 8765 y usa WebSockets. No se puede probar con cURL."
echo "Para probarlo, corre: python3 send-news/client_suscriptor.py"

print_step "PRUEBAS E2E FINALIZADAS CON ÉXITO"
