# Usamos la versión Alpine de Postgres 16 (liviana y segura)
FROM postgres:16-alpine

LABEL maintainer="Ingeniería de Software"
LABEL version="1.0-pg"

# Seteamos el idioma por defecto (útil para el ordenamiento de strings)
ENV LANG es_AR.utf8

# Copiamos los scripts. Postgres también usa este directorio mágico.
# Los ejecutará en orden alfabético.
COPY ./scripts/ /docker-entrypoint-initdb.d/