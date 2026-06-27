# Consorcio de Noticias - Sistemas Distribuidos (2026)

Este repositorio contiene el proyecto práctico para la materia **Sistemas Distribuidos (2do Cuatrimestre 2026)**. La arquitectura del sistema consiste en un conjunto de microservicios independientes y desacoplados que cooperan para formar un consorcio de noticias distribuido.

Todos los servicios comparten una única base de datos PostgreSQL centralizada y se comunican a través de la red de Docker compartida `consorcio-red`.

---

## 🏛️ Microservicios del Proyecto

A continuación, se detalla la funcionalidad, estructura y cómo desplegar cada uno de los microservicios del consorcio:

### 1. Base de Datos (`database`)
- **Funcionalidad:** Base de datos PostgreSQL centralizada. Provee los esquemas iniciales y datos de prueba para todos los microservicios del proyecto.
- **Estructura:** Contiene los scripts SQL de inicialización en la carpeta `scripts/` y su propio `docker-compose.yml` para levantar la instancia en el puerto `5432`.
- **Despliegue:**
  ```bash
  docker compose -f database/docker-compose.yml up -d
  ```

### 2. Buscar Noticias por Descriptor (`find-news-by-descriptor`)
- **Funcionalidad:** Servicio gRPC (Python) que busca noticias a partir de un descriptor (mínimo 3 caracteres), utilizando *PostgreSQL Full-Text Search* para optimizar coincidencias ignorando conectores o plurales.
- **Estructura:** Código plano. Archivos ubicados en la raíz de `find-news-by-descriptor/` (cliente interactivo, servidor gRPC y contratos proto).
- **Despliegue:** (Requiere la base de datos central iniciada primero)
  ```bash
  docker compose -f find-news-by-descriptor/docker-compose.yml up -d --build
  ```
  _Para probar el cliente interactivo localmente, se puede utilizar el shortcut `.\find-news-by-descriptor\run_client.bat`._

### 3. Gestión de Áreas (`area-manager`)
- **Funcionalidad:** API REST (Go) encargada de la gestión (creación y eliminación) de áreas o categorías temáticas.
- **Estructura:** Código fuente unificado en `main.go`. Incluye un `test.bash` para probar los endpoints interactuando con la API (puerto `8080`).
- **Despliegue:** (Requiere la base de datos central iniciada primero)
  ```bash
  docker compose -f area-manager/docker-compose.yml up -d --build
  ```

### 4. Búsqueda de Noticias por Período (`find-news-period`)
- **Funcionalidad:** Servicio (Python) para obtener noticias publicadas dentro de un rango de tiempo específico.
- **Estructura:** API desarrollada en Python, con los archivos fuente directamente en la raíz de la carpeta.
- **Despliegue:** (Requiere la base de datos central iniciada primero. Expone el puerto `8010`):
  ```bash
  docker compose -f find-news-period/docker-compose.yml up -d --build
  ```

### 5. Carga de Noticias por Área (`get-news-load-by-area`)
- **Funcionalidad:** Servicio (Python) que proporciona estadísticas sobre la cantidad de noticias publicadas por cada área temática.
- **Estructura:** API en Python con sus scripts ubicados de forma plana en la raíz de su respectiva carpeta.
- **Despliegue:** (Requiere la base de datos central iniciada primero. Expone el puerto `8020`):
  ```bash
  docker compose -f get-news-load-by-area/docker-compose.yml up -d --build
  ```

### 6. Borrado de Noticias (`delete-news`)
- **Funcionalidad:** API REST (Python/FastAPI) que permite a un usuario eliminar una noticia del consorcio, validando previamente que el usuario solicitante (`user_id`) sea el autor original de la misma.
- **Estructura:** Servidor FastAPI en `server.py`, dependencias en `requirements.txt` y Dockerfile. Cuenta con su propio `docker-compose.yml` que levanta tanto el servicio en el puerto `8000` como una base de datos PostgreSQL local para pruebas.
- **Despliegue:** (Expone el puerto `8000`):
  ```bash
  docker compose -f delete-news/docker-compose.yml up -d --build
  ```

### 7. Gestión de Suscripciones (`new_subscriptions`)
- **Funcionalidad:** API REST (Python/FastAPI) para gestionar la suscripción y desuscripción de clientes a áreas temáticas de noticias, además de permitir la creación y el listado de áreas en la base de datos central.
- **Estructura:** Archivos de código fuente distribuidos de forma plana (`subscribe.py`), junto a su respectivo `Dockerfile`, `requirements.txt` y un archivo `docker-compose.yml` configurado para conectarse a la base de datos central y exponer el puerto `8030`.
- **Despliegue:** (Requiere la base de datos central iniciada primero. Expone el puerto `8030`):
  ```bash
  docker compose -f new_subscriptions/docker-compose.yml up -d --build
  ```

### 8. Envío de Noticias (`send-news`)
- **Funcionalidad:** Servicio de mensajería Pub/Sub WebSocket (Python) que permite a los clientes suscribirse a una sección para recibir noticias en tiempo real (streaming asíncrono).
- **Estructura:** Servidor WebSocket en `server.py`, cliente de suscripción en `client_suscriptor.py`, dependencias en `requirements.txt` y `Dockerfile`.
- **Despliegue:** (Expone el puerto `8765` para conexiones WebSocket):
  ```bash
  docker compose -f send-news/docker-compose.yml up -d --build
  ```

---

## 🛑 Detener los Servicios

Para apagar cualquiera de los entornos que utilizan Docker Compose:

```bash
docker compose -f <carpeta>/docker-compose.yml down
```

