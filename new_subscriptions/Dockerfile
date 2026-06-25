# Usamos una imagen liviana de Python
FROM python:3.11-slim

# Seteamos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copiamos requerimientos y los instalamos
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiamos el código
COPY . /app/

# Exponemos el puerto de FastAPI
EXPOSE 8000

# Ejecutamos con uvicorn apuntando a host 0.0.0.0
CMD ["uvicorn", "subscribe:app", "--host", "0.0.0.0", "--port", "8000"]