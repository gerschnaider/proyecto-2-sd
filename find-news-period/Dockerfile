# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc / __pycache__
ENV PYTHONDONTWRITEBYTECODE=1

# Log fluido
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código
COPY . .

# Comando para arrancar FastAPI
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]