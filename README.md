# Consorcio de Noticias - Servicio de Búsqueda por Descriptor (Sistemas Distribuidos 2026)

Implementación del **Servicio 7: Buscar noticias con un descriptor**.

Desarrollado en **Python** utilizando **gRPC** para la comunicación sincrónica interna y **PostgreSQL** como base de datos centralizada con soporte para búsquedas de texto completo (Full-Text Search).

---

## 📂 Estructura del Repositorio

```text
├── database/                   # Contenedor y scripts SQL
│   ├── scripts/                # Esquemas iniciales y datos de prueba
│   ├── Dockerfile              # Imagen Postgres 16 Alpine
│   └── docker-compose.yml      # Compose para levantar la base de datos
│
├── news_search/                # Archivos del microservicio de búsqueda gRPC
│   ├── src/                    # Código de servidor, cliente y base de datos
│   ├── protos/                 # Contrato e interfaces de Protocol Buffers
│   ├── Dockerfile              # Imagen optimizada de Python 3.11-slim
│   ├── requirements.txt        # Librerías de Python requeridas
│   └── docker-compose.yml      # Compose para el servicio de búsqueda
│
├── run_client.bat              # Script de atajo para ejecutar el cliente interactivo
├── AIContext.md                # Bitácora e historial de estado del proyecto para IA
└── README.md                   # Documentación
```

---

## 🚀 Despliegue con Docker Compose

### 1. Iniciar la Base de Datos

```bash
docker compose -f database/docker-compose.yml up -d
```

_Este comando levantará Postgres (puerto `5432`), creará la red `consorcio-red` e inyectará los esquemas y datos de prueba de manera automática._

### 2. Iniciar el Servidor de Búsqueda gRPC

Una vez que Postgres esté listo, levanta el microservicio de búsqueda:

```bash
docker compose -f news_search/docker-compose.yml up -d --build
```

_Este comando compilará la imagen en Python, se unirá a la red virtual de base de datos y levantará el servidor gRPC en el puerto `50051`._

### 3. Ejecutar el Cliente

```powershell
.\run_client.bat
```

_Este script ejecutará directamente el cliente interactivo sin necesidad de activar manualmente el entorno virtual en la terminal._

### 4. Detener los Servicios

```bash
docker compose -f news_search/docker-compose.yml down
docker compose -f database/docker-compose.yml down
```

---

## 🔍 Detalles Técnicos

Para evitar problemas de falsos positivos en búsquedas muy genéricas (como vocales o conectores), se implementó un motor de búsqueda avanzado combinando:

1.  **Validación en Cliente:** El cliente gRPC valida que el término de búsqueda contenga un mínimo de **3 caracteres** antes de enviarlo al servidor.
2.  **PostgreSQL Full-Text Search:** El archivo `src/db.py` realiza consultas utilizando `to_tsvector` y `plainto_tsquery` en idioma español (`spanish`). Esto permite:
    - Ignorar conectores irrelevantes (ej. _de_, _el_, _a_, _y_).
    - Soportar plurales/singulares y derivaciones raíz de palabras (ej. buscar _deporte_ coincidirá con _deportes_ y _deportivo_).
    - Buscar coincidencias indexadas en el título, contenido y nombre de categoría de la noticia mediante un `JOIN`.
