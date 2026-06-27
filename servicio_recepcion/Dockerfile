FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 50050

# Comando que se ejecuta automáticamente al encender el contenedor
CMD ["python", "-u", "servidor_receptor.py"]