# Consorcio de Noticias - Servicio de Búsqueda por Descriptor (Sistemas Distribuidos 2026)

Este repositorio contiene la implementación del **Servicio 7: Buscar noticias con un descriptor**, asignado a Manuel Tauro para el proyecto de la materia de Sistemas Distribuidos (2026).

El servicio está desarrollado en **Python** utilizando **gRPC** para la comunicación sincrónica interna y **PostgreSQL** como base de datos centralizada con soporte para búsquedas de texto completo (Full-Text Search).

---

## 📂 Estructura del Repositorio

El proyecto ha sido modularizado para independizar el ciclo de vida de la base de datos de pruebas del microservicio de código:

```text
├── database/                   # Contenedor y scripts de inicialización SQL
│   ├── scripts/                # Esquemas iniciales y datos de prueba
│   ├── Dockerfile              # Imagen Postgres 16 Alpine
│   └── docker-compose.yml      # Compose exclusivo para levantar la base de datos
│
├── news_search/                # Archivos del microservicio de búsqueda gRPC
│   ├── src/                    # Código de servidor, cliente y base de datos
│   ├── protos/                 # Contrato e interfaces de Protocol Buffers
│   ├── Dockerfile              # Imagen optimizada de Python 3.11-slim
│   ├── requirements.txt        # Librerías de Python requeridas
│   └── docker-compose.yml      # Compose exclusivo para el servicio de búsqueda
│
├── run_client.bat              # Script de atajo para ejecutar el cliente interactivo
├── AIContext.md                # Bitácora e historial de estado del proyecto para IA
└── README.md                   # Esta documentación
```

---

## 🚀 Despliegue con Docker Compose (Independiente)

Los entornos de Docker Compose se comunican a través de una red virtual compartida llamada `consorcio-red`. Debes levantarlos en el siguiente orden:

### 1. Iniciar la Base de Datos
Desde la raíz del proyecto, ejecuta:
```bash
docker compose -f database/docker-compose.yml up -d
```
*Este comando levantará Postgres (puerto `5432`), creará la red `consorcio-red` e inyectará los esquemas y datos de prueba de manera automática.*

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
..\.venv\Scripts\python.exe src/server.py
```

### Ejecutar el Cliente Interactivo (Shortcut)
Para probar búsquedas en tiempo real de forma fácil, corre el script batch desde la raíz del proyecto:
```powershell
.\run_client.bat
```
*Este script ejecutará directamente el cliente interactivo sin necesidad de activar manualmente tu entorno virtual en la terminal.*

---

## 🔍 Detalles Técnicos del Motor de Búsqueda

Para evitar problemas de falsos positivos en búsquedas muy genéricas (como vocales o conectores), se implementó un motor de búsqueda avanzado combinando:

1.  **Validación en Cliente:** El cliente gRPC valida que el término de búsqueda contenga un mínimo de **3 caracteres** antes de enviarlo al servidor.
2.  **PostgreSQL Full-Text Search:** El archivo `src/db.py` realiza consultas utilizando `to_tsvector` y `plainto_tsquery` en idioma español (`spanish`). Esto permite:
    *   Ignorar conectores irrelevantes (ej. *de*, *el*, *a*, *y*).
    *   Soportar plurales/singulares y derivaciones raíz de palabras (ej. buscar *deporte* coincidirá con *deportes* y *deportivo*).
    *   Buscar coincidencias indexadas en el título, contenido y nombre de categoría de la noticia mediante un `JOIN`.
