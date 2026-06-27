FROM python:3.9-slim

WORKDIR /app

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar las librerías de python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Exponer el puerto del servidor WebSocket
EXPOSE 8765

# Comando para correr el servidor
CMD ["python", "server.py"]
