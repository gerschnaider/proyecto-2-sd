.PHONY: help build deploy down ps logs test clean local-up local-down

# IP por defecto para los tests, se puede sobreescribir usando: make test IP=192.168.x.x
IP ?= localhost

help:
	@echo "======================================================================"
	@echo "        Consorcio de Noticias - Comandos de Despliegue (Make)         "
	@echo "======================================================================"
	@echo "--- COMANDOS PARA DOCKER SWARM (CLÚSTER) ---"
	@echo "make build       - Construye las imágenes de Docker localmente"
	@echo "make deploy      - Despliega el proyecto en Docker Swarm (crea el stack)"
	@echo "make down        - Detiene y elimina el stack de Docker Swarm"
	@echo "make ps          - Muestra el estado y réplicas de los servicios"
	@echo ""
	@echo "--- COMANDOS PARA ENTORNO LOCAL (SIN SWARM) ---"
	@echo "make local-up    - Levanta todos los servicios localmente con Docker Compose"
	@echo "make local-down  - Baja los servicios locales de Docker Compose"
	@echo ""
	@echo "--- UTILIDADES ---"
	@echo "make test        - Ejecuta las pruebas E2E (usa 'make test IP=x.x.x.x' para red remota)"
	@echo "make clean       - Borra el stack y limpia imágenes/contenedores en desuso"
	@echo "======================================================================"

# ==========================================
# COMANDOS DOCKER SWARM
# ==========================================
build:
	@echo "Construyendo las imágenes de los microservicios..."
	docker compose build

deploy:
	@echo "Desplegando el stack 'consorcio' en Docker Swarm..."
	docker stack deploy -c docker-compose.yml consorcio

down:
	@echo "Eliminando el stack 'consorcio'..."
	docker stack rm consorcio

ps:
	@echo "Lista de servicios:"
	docker service ls
	@echo "\nEstado de las réplicas:"
	docker stack ps consorcio

# ==========================================
# COMANDOS LOCALES (DOCKER COMPOSE)
# ==========================================
local-up:
	@echo "Levantando el entorno local..."
	docker compose up -d --build

local-down:
	@echo "Bajando el entorno local..."
	docker compose down

# ==========================================
# PRUEBAS Y LIMPIEZA
# ==========================================
test:
	@if [ "$(IP)" = "localhost" ]; then \
		read -p "Ingrese la IP del clúster Swarm (o ENTER para 'localhost'): " user_ip; \
		IP_TO_USE=$${user_ip:-localhost}; \
	else \
		IP_TO_USE="$(IP)"; \
	fi; \
	echo "Ejecutando batería de pruebas E2E contra: $$IP_TO_USE"; \
	chmod +x e2e_test.sh; \
	./e2e_test.sh $$IP_TO_USE


clean: down
	@echo "Limpiando el sistema Docker (prune)..."
	docker system prune -f
