# Consorcio de Noticias - Sistemas Distribuidos (2026)

Este repositorio contiene el proyecto práctico para la materia **Sistemas Distribuidos (2026)**. La arquitectura del sistema consiste en un conjunto de microservicios independientes y desacoplados que cooperan para formar un consorcio de noticias distribuido.

---

## 🏛️ Microservicios del Proyecto

*   **[database](file:///c:/Users/manut/Documentos/UNIVERSIDAD/2026/Sistemas%20Distribuidos/proyecto-2-sd/database)**: Base de datos PostgreSQL centralizada con esquemas y datos iniciales de prueba.
*   **[news_search](file:///c:/Users/manut/Documentos/UNIVERSIDAD/2026/Sistemas%20Distribuidos/proyecto-2-sd/news_search)**: Servicio 7: Buscar noticias con un descriptor (desarrollado en Python con gRPC).
*   **[area-manager](file:///c:/Users/manut/Documentos/UNIVERSIDAD/2026/Sistemas%20Distribuidos/proyecto-2-sd/area-manager)**: Gestión de áreas/categorías temáticas (desarrollado en Go).
*   **[find_news_period](file:///c:/Users/manut/Documentos/UNIVERSIDAD/2026/Sistemas%20Distribuidos/proyecto-2-sd/find_news_period)**: Servicio de búsqueda de noticias por período de tiempo (desarrollado en Python).
*   **[get-news-load-by-area](file:///c:/Users/manut/Documentos/UNIVERSIDAD/2026/Sistemas%20Distribuidos/proyecto-2-sd/get-news-load-by-area)**: Estadísticas de carga de noticias por áreas (desarrollado en Python).

---

## 📂 Estructura del Servicio de Búsqueda (`news_search`)

Siguiendo la convención adoptada por el equipo, los archivos del microservicio se ubican directamente en la raíz de su carpeta:

```text
├── database/                   # Contenedor y scripts SQL
│   ├── scripts/                # Esquemas iniciales y datos de prueba
│   ├── Dockerfile              # Imagen Postgres 16 Alpine
│   └── docker-compose.yml      # Compose para levantar la base de datos
│
├── news_search/                # Archivos del microservicio de búsqueda gRPC
│   ├── protos/                 # Contrato e interfaces de Protocol Buffers
│   ├── client.py               # Cliente gRPC de testeo interactivo
│   ├── db.py                   # Conexión y consultas a la base de datos
│   ├── server.py               # Servidor gRPC principal
│   ├── Dockerfile              # Imagen optimizada de Python 3.11-slim
│   ├── requirements.txt        # Librerías de Python requeridas
│   └── docker-compose.yml      # Compose para el servicio de búsqueda
│
├── run_client.bat              # Script de atajo para ejecutar el cliente interactivo
├── AIContext.md                # Bitácora de estado del proyecto para IA
└── README.md                   # Esta documentación global
```

---

## 🚀 Despliegue con Docker Compose (Servicio de Búsqueda)

Los entornos de Docker Compose se comunican a través de una red virtual compartida llamada `consorcio-red`. Debes levantarlos en el siguiente orden:

### 1. Iniciar la Base de Datos
Desde la raíz del proyecto, ejecuta:
```bash
docker compose -f database/docker-compose.yml up -d
```
*Este comando levantará Postgres (puerto `5432`), creará la red `consorcio-red` e inyectará los esquemas y datos de prueba.*

### 2. Iniciar el Servidor de Búsqueda gRPC
Una vez que Postgres esté listo, levanta el microservicio de búsqueda:
```bash
docker compose -f news_search/docker-compose.yml up -d --build
```
*Este comando compilará la imagen en Python, se unirá a la red virtual de base de datos y levantará el servidor gRPC en el puerto `50051`.*

### 3. Detener los Servicios
Para apagar el entorno de forma limpia y liberar los puertos:
```bash
docker compose -f news_search/docker-compose.yml down
docker compose -f database/docker-compose.yml down
```

---

## 🛠️ Desarrollo Local (Sin Docker)

Si deseas depurar el servidor gRPC o ejecutar el cliente directamente en tu sistema operativo local:

### Requisitos Previos (Windows)
Asegúrate de tener un entorno virtual configurado en la raíz del proyecto.
1. Crear el entorno virtual:
   ```powershell
   python -m venv .venv
   ```
2. Instalar dependencias en el entorno virtual:
   ```powershell
   .venv\Scripts\pip install -r news_search/requirements.txt
   ```

### Ejecutar el Servidor Localmente
Asegúrate de que la base de datos de Docker esté levantada y ejecuta:
```powershell
# Desde la carpeta news_search
cd news_search
..\.venv\Scripts\python.exe server.py
```

### Ejecutar el Cliente Interactivo (Shortcut)
Para probar búsquedas en tiempo real de forma fácil, corre el script batch desde la raíz del proyecto:
```powershell
.\run_client.bat
```
*Este script ejecutará directamente el cliente interactivo sin necesidad de activar manualmente el entorno virtual en la terminal.*

---

## 🔍 Detalles Técnicos del Motor de Búsqueda

Para evitar problemas de falsos positivos en búsquedas muy genéricas (como vocales o conectores), se implementó un motor de búsqueda avanzado combinando:

1.  **Validación en Cliente:** El cliente gRPC valida que el término de búsqueda contenga un mínimo de **3 caracteres** antes de enviarlo al servidor.
2.  **PostgreSQL Full-Text Search:** El archivo `news_search/db.py` realiza consultas utilizando `to_tsvector` y `plainto_tsquery` en idioma español (`spanish`). Esto permite:
    *   Ignorar conectores irrelevantes (ej. _de_, _el_, _a_, _y_).
    *   Soportar plurales/singulares y derivaciones raíz de palabras (ej. buscar _deporte_ coincidirá con _deportes_ y _deportivo_).
    *   Buscar coincidencias indexadas en el título, contenido y nombre de categoría de la noticia mediante un `JOIN`.
