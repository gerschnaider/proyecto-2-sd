# Contexto del Proyecto

## Estado General
Estamos desarrollando el Segundo Proyecto de la materia Sistemas Distribuidos (2026). El objetivo es crear un Consorcio de Noticias distribuido y tolerante a fallos usando gRPC y Docker Swarm.
Actualmente hemos completado la implementación del microservicio asignado a Manuel Tauro: **"Buscar noticias con un descriptor"**.

## Arquitectura y Decisiones
- **Servicio de Búsqueda:** Implementado en Python 3.11, con comunicación sincrónica mediante gRPC (puerto 50051). Contrato gRPC en `news_search/protos/news_search.proto`.
- **Base de Datos:** PostgreSQL 16 Alpine centralizado, ejecutado en su propio contenedor (puerto 5432) con scripts de inicialización y datos de prueba.
- **Estructura de Carpetas:**
  - `database/`: Contenedor y scripts SQL de inicialización.
  - `news_search/`: Contiene todo lo relativo al servicio de búsqueda (código fuente en `src/`, firmas gRPC en `protos/`, Dockerfile y requirements.txt).
  - `graphify-out/`: Único directorio en la raíz para la documentación visual de la arquitectura.
- **Docker Compose:** Configurado en `docker-compose.yml` para levantar tanto la base de datos como el servicio de búsqueda localmente, utilizando variables de entorno parametrizadas con valores por defecto (ej. `DB_HOST=${DB_HOST:-database}`) para máxima portabilidad.

## Tareas Completadas (Recientes)
- [x] Limpieza de carpetas duplicadas de Graphify y archivos obsoletos.
- [x] Aislamiento del servicio de búsqueda en el subdirectorio autocontenido `news_search/`.
- [x] Configuración del Dockerfile en `news_search/` y vinculación en `docker-compose.yml`.
- [x] Flexibilización de variables de conexión (`DB_HOST`, etc.) en Docker Compose.
- [x] Verificación de la compilación y conectividad de los contenedores Docker locales.

## Próximos Pasos (TODO)
- [ ] Integrar el microservicio con el proxy reverso / balanceador de carga global del proyecto.
- [ ] Configurar el despliegue final en la infraestructura Docker Swarm del grupo.
- [ ] Coordinar con los compañeros para la unificación de los esquemas e interconexión de otros servicios.

## Problemas Abiertos o Notas
- La búsqueda realiza una coincidencia precisa por palabras, categorías o contenido usando el motor PostgreSQL Full-Text Search en español.
