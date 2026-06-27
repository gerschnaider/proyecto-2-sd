# Usamos una imagen oficial y ligera de Python
FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="Servicio de Borrado de Noticias"

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos de requerimientos primero (optimiza la caché de Docker)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente de nuestro servidor
COPY server.py .

# Exponemos el puerto donde correrá FastAPI
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
