# Contexto del Proyecto

## Estado General
Estamos desarrollando el Segundo Proyecto de la materia Sistemas Distribuidos (2026). El objetivo es crear un Consorcio de Noticias distribuido y tolerante a fallos usando gRPC y Docker Swarm.
Actualmente el proyecto cuenta con múltiples microservicios desacoplados: búsqueda de noticias (gRPC), gestor de áreas (REST), búsqueda por período (REST), carga de noticias (REST), borrado de noticias (REST), suscripciones (REST) y envío de noticias (gRPC Pub/Sub).

## Arquitectura y Decisiones
- **Base de Datos:** PostgreSQL centralizado (`database/`), ejecutado en su propio contenedor (puerto 5432) con scripts de inicialización y datos de prueba. Todos los servicios con persistencia se conectan a él.
- **Servicios Principales:**
  - `find-news-by-descriptor/`: Servicio gRPC (Python) en puerto 50051 para búsquedas por descriptores usando PostgreSQL Full-Text Search.
  - `area-manager/`: API REST (Go) en puerto 8080 para la gestión de áreas/categorías.
  - `find-news-period/`: API REST (Python) en puerto 8010 para buscar noticias por rango temporal.
  - `get-news-load-by-area/`: API REST (Python) en puerto 8020 para estadísticas de volumen de noticias.
  - `delete-news/`: API REST (Python) en puerto 8000 para eliminación de noticias asegurando autoría del creador.
  - `new_subscriptions/`: API REST (Python) en puerto 8030 para gestionar suscripciones de usuarios a áreas temáticas.
  - `send-news/`: Servicio de mensajería Pub/Sub WebSocket (Python) en puerto 8765 para suscripción asíncrona (streaming).
- **Red Compartida:** Docker bridge `consorcio-red` para la intercomunicación de servicios.
- **Documentación de Arquitectura:** Directorio `graphify-out/` generado dinámicamente con `graphify`.

## Tareas Completadas (Recientes)
- [x] Limpieza de carpetas duplicadas de Graphify y archivos obsoletos.
- [x] Configuración de Dockerfiles y docker-compose.yml parametrizados por servicio.
- [x] Creación de `docker-compose.yml` para `new_subscriptions` y vinculación a `consorcio-red`.
- [x] Actualización del `README.md` principal para reflejar y unificar las instrucciones de todos los servicios del consorcio.
- [x] Sincronización del grafo de dependencias y arquitectura del proyecto con `graphify update .`.

## Próximos Pasos (TODO)
- [ ] Integrar el microservicio con el proxy reverso / balanceador de carga global del proyecto.
- [ ] Configurar el despliegue final en la infraestructura Docker Swarm del grupo.
- [ ] Coordinar con los compañeros para la unificación de los esquemas e interconexión de otros servicios.

## Problemas Abiertos o Notas
- Las búsquedas realizan coincidencias precisas por palabras, categorías o contenido usando el motor PostgreSQL Full-Text Search en español.
- **Incompatibilidad en `delete-news`:** El archivo `delete-news/docker-compose.yml` aún cuenta con un contenedor local de PostgreSQL redundante que colisiona en el puerto `5432` y no se conecta a la red compartida `consorcio-red` ni a la base de datos centralizada.


