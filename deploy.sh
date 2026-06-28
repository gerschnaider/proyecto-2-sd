#!/bin/bash

# ==============================================================================
# SCRIPT DE DESPLIEGUE automatizado para DOCKER SWARM
# ==============================================================================

set -e

echo -e "\n=== 1. Construyendo imágenes locales para Swarm ==="
docker compose build

echo -e "\n=== 2. Desplegando el stack 'consorcio' en Docker Swarm ==="
docker stack deploy -c docker-compose.yml consorcio

echo -e "\n=== ¡Despliegue completado! ==="
echo "Puedes verificar el estado de los servicios ejecutando: docker stack services consorcio"
