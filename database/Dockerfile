# Usamos la versión Alpine de Postgres 16 (liviana y segura)
FROM postgres:16-alpine

# Seteamos el idioma por defecto (útil para el ordenamiento de strings)
ENV LANG es_AR.utf8

# Copiamos los scripts. Postgres también usa este directorio mágico.
COPY ./scripts/ /docker-entrypoint-initdb.d/