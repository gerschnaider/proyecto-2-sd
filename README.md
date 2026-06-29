# Consorcio de Noticias - Sistemas Distribuidos (2026)

Este repositorio contiene el proyecto final integrador para la materia **Sistemas Distribuidos (2do Cuatrimestre 2026)**. El sistema implementa un consorcio de noticias distribuido, diseñado bajo una arquitectura de microservicios independientes, resilientes y altamente acoplados a través de una red virtual en clúster.

---

## 🏛️ Arquitectura del Sistema

El sistema ha sido diseñado priorizando la escalabilidad, la consistencia de los datos y la estandarización de las comunicaciones:

- **Ecosistema de Microservicios:** 9 servicios independientes desarrollados en Python y Go.
- **Comunicación Estándar (REST):** Todos los microservicios exponen APIs HTTP/REST para garantizar una integración fluida y uniforme. Durante el desarrollo se migró infraestructura legacy (como gRPC) hacia este estándar.
- **Base de Datos Centralizada:** Instancia relacional PostgreSQL compartida que asegura un único punto de verdad, controlando transacciones y concurrencia.
- **Despliegue Multi-Nodo (Docker Swarm):** Los servicios están orquestados con Docker Swarm, comunicándose a través de la red overlay `consorcio-red`. Esto permite escalado horizontal y alta disponibilidad de los contenedores distribuidos en una VPN (ZeroTier / Hamachi).

---

## 🧠 Decisiones de Diseño y Patrones

### 1. Borrado Lógico (Soft Delete) y Cascada
Para mantener la integridad histórica y referencial del consorcio, el sistema implementa un mecanismo estricto de **borrado lógico** mediante el flag `is_deleted = true`.
- Cuando el microservicio `area-manager` elimina una categoría, no borra el registro físico de la base de datos, sino que lo apaga lógicamente.
- **Cascada Programática:** Esta acción desencadena de forma automática y transaccional el apagado lógico de todas las noticias (`news`) pertenecientes a esa área.
- **Restricciones de Unicidad:** Las categorías (áreas) mantienen restricciones `UNIQUE` sobre su nombre. Esta decisión de diseño previene la creación de categorías duplicadas, incluso si la original se encuentra en estado de borrado lógico.

### 2. Control de Concurrencia Optimista
El servicio de gestión de áreas implementa un control de concurrencia avanzado para proteger la consistencia de los datos en un ambiente distribuido de alta demanda:
- Transacciones configuradas estrictamente en nivel **`SERIALIZABLE`**.
- Tolerancia a fallos mediante mecanismos de **Retry con Exponential Backoff**. Si PostgreSQL detecta un fallo de serialización por carrera de condiciones o un *deadlock* (códigos `40001` o `40P01`), el microservicio intercepta el error, aborta y reintenta la transacción automáticamente de forma transparente para el usuario.

---

## ⚙️ Microservicios del Proyecto

### 1. Base de Datos (`database`)
- **Rol:** PostgreSQL centralizada. Provee los esquemas iniciales (`01-scheme.sql`), tablas, restricciones referenciales y los datos de prueba iniciales (seed).
- **Puerto Externo:** `5432`

### 2. Gestión de Áreas (`area-manager`)
- **Rol:** API REST (Go) de alta concurrencia encargada de crear y eliminar (borrado lógico en cascada) áreas temáticas, validando permisos de autoría.
- **Puerto Externo:** `8080`

### 3. Borrado de Noticias (`delete-news`)
- **Rol:** API REST (FastAPI) que permite a un usuario eliminar de forma individual una noticia (borrado lógico), validando previamente que el usuario solicitante (`user_id`) sea el creador original de la misma.
- **Puerto Externo:** `8001`

### 4. Búsqueda de Noticias por Período (`find-news-period`)
- **Rol:** API REST (Python) para obtener un listado cronológico de noticias publicadas dentro de un rango de tiempo delimitado (`fecha_inicio` a `fecha_fin`).
- **Puerto Externo:** `8002`

### 5. Carga de Noticias por Área (`get-news-load-by-area`)
- **Rol:** API REST (Python) que genera estadísticas y métricas, proporcionando el conteo total de noticias activas agrupadas por cada área temática.
- **Puerto Externo:** `8003`

### 6. Gestión de Suscripciones (`new_subscriptions`)
- **Rol:** API REST (FastAPI) encargada de suscribir y desuscribir usuarios a áreas temáticas de noticias. Verifica estrictamente que el área solicitada exista y se encuentre activa (no eliminada).
- **Puerto Externo:** `8004`

### 7. Noticias de las Últimas 24hs (`last-news-24-hour`)
- **Rol:** API REST que devuelve el flujo de noticias recientes publicadas exclusivamente en las áreas a las que un usuario particular se encuentra suscrito.
- **Puerto Externo:** `8005`

### 8. Buscar Noticias por Descriptor (`find-news-by-descriptor`)
- **Rol:** API REST (FastAPI) que realiza búsquedas semánticas de noticias a partir de palabras clave (descriptores), utilizando *PostgreSQL Full-Text Search* y omitiendo registros con borrado lógico.
- **Puerto Externo:** `8030`

### 9. Servicio de Recepción y Envío (`send-news` / `servicio_recepcion`)
- **Rol:** Actúa como Publicador REST para la ingesta general de noticias (puerto `50050`) y como servidor Pub/Sub basado en **WebSockets** (puerto `8765`) para transmitir notificaciones en tiempo real a los clientes suscritos.

---

## 🚀 Despliegue y Pruebas

### Despliegue Global en Docker Swarm
El ecosistema entero se despliega utilizando el manifiesto unificado `docker-compose.yml` ubicado en la raíz del proyecto, el cual orquesta las imágenes distribuidas en el clúster.

```bash
docker stack deploy -c docker-compose.yml consorcio
```
*(Nota: Algunos microservicios están condicionados mediante `placement constraints` a ejecutarse obligatoriamente en nodos Manager, como la Raspberry Pi).*

### Batería de Pruebas E2E Automatizadas
El repositorio cuenta con el script interactivo de validación de sistema `e2e_test.sh`. Este test de integración simula el flujo de vida completo de un usuario:

1. Creación dinámica de un área temática.
2. Suscripción de un usuario al área recién creada.
3. Ingesta y publicación de una noticia de prueba, verificando validaciones.
4. Ejecución paralela de búsquedas semánticas, métricas temporales y conteo de carga.
5. Aplicación del borrado lógico en cascada para limpiar el estado de la base de datos tras finalizar.

**Modo de Uso:**
Para disparar la batería de pruebas contra la IP del clúster (requiere herramienta `jq`):
```bash
./e2e_test.sh <IP_DEL_SWARM_O_LOCAL>
```

---

## 🛑 Detener los Servicios (Entornos Locales)

Para bajar los contenedores en desarrollos aislados utilizando Docker Compose clásico:
```bash
docker compose -f <carpeta>/docker-compose.yml down
```
