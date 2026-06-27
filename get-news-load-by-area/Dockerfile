# Usa una imagen oficial de Python ligera
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Fernando Champredonde"
LABEL version="1.0"

# Crea un directorio de trabajo en el contenedor
WORKDIR /app

# Copia primero los requirements para aprovechar el cache de capas de Docker
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente al contenedor
COPY . .

# Expone el puerto donde corre la aplicación
EXPOSE 8000

# Comando para ejecutar el servidor con uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
