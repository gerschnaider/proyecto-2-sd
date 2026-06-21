# 1. Usamos una imagen oficial de Python liviana (slim) como base
FROM python:3.11-slim

# 2. Configuraciones de entorno optimizadas para contenedores
# Evita que Python escriba archivos temporales .pyc en el disco del contenedor
ENV PYTHONDONTWRITEBYTECODE=1
# Hace que Python envíe los logs de print() directo a la consola sin acumularlos en buffer
ENV PYTHONUNBUFFERED=1

# 3. Definimos cuál será la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos la lista de dependencias al contenedor
COPY requirements.txt .

# 5. Instalamos las dependencias
# --no-cache-dir evita guardar los instaladores descargados, haciendo la imagen mucho más liviana
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el código de nuestro microservicio y las firmas de gRPC
COPY src/ ./src/
COPY protos/ ./protos/

# 7. Informamos a Docker que este contenedor escuchará en el puerto 50051
EXPOSE 50051

# 8. El comando que se ejecutará cuando el contenedor arranque
CMD ["python", "src/server.py"]
