FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para grpc
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar las librerías de python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Compilar los archivos protobuf a python
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. noticias.proto

# Exponer el puerto donde escucha el servidor gRPC
EXPOSE 50051

# Comando para correr el servidor
CMD ["python", "server.py"]
