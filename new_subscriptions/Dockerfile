FROM python:3.11-slim

WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#requerimientos
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app/

#puerto de FastAPI
EXPOSE 8000

# Ejecutar uvicorn
CMD ["uvicorn", "subscribe:app", "--host", "0.0.0.0", "--port", "8000"]