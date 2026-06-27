# Guía de Uso de la API - `last-news-24-hour`

Este microservicio en FastAPI expone endpoints HTTP para consultar las noticias publicadas en las últimas 24 horas, ofreciendo soporte para filtrado personalizado según las suscripciones de cada usuario y resiliencia mediante fallbacks automáticos.

## 📌 Endpoints Disponibles

### 1. Estado de Salud (`GET /health`)
Verifica que el microservicio esté activo y respondiendo.

- **URL:** `/health`
- **Método:** `GET`
- **Ejemplo `curl`:**
  ```bash
  curl -i http://localhost:8000/health
  ```
- **Respuesta Esperada (`200 OK`):**
  ```json
  {
    "status": "ok"
  }
  ```

---

### 2. Noticias de las Últimas 24 Horas (`GET /api/news-last-24h`)
Devuelve el listado de noticias publicadas en las últimas 24 horas.

- **URL:** `/api/news-last-24h`
- **Método:** `GET`
- **Parámetros Query (Opcionales):**
  | Parámetro | Tipo | Descripción | Ejemplo |
  | :--- | :--- | :--- | :--- |
  | `user_id` | `integer` | ID del usuario para filtrar las noticias según sus áreas/categorías suscriptas. | `?user_id=2` |

---

#### 💡 Ejemplo A: Consulta General (Sin parámetros)
Obtiene todas las noticias publicadas en las últimas 24 horas sin restricciones.

**Comando `curl`:**
```bash
curl -s http://localhost:8000/api/news-last-24h | jq .
```

**Respuesta Esperada (`200 OK`):**
```json
[
  {
    "news_id": 5,
    "title": "Reunión del Centro de Estudiantes",
    "content": "Hoy a las 18hs se debate el nuevo plan de estudios.",
    "category_name": "Centro de Estudiantes",
    "created_at": "2026-06-27T22:19:52.690092"
  },
  {
    "news_id": 1,
    "title": "Nuevas integraciones para Home Assistant",
    "content": "Se publicaron actualizaciones para ESPHome.",
    "category_name": "Tecnología y UNS",
    "created_at": "2026-06-27T21:49:52.690092"
  }
]
```

---

#### 💡 Ejemplo B: Consulta Filtrada por Usuario (`user_id`)
Obtiene únicamente las noticias de las últimas 24 horas pertenecientes a las categorías a las cuales el usuario especificado se encuentra suscripto.

**Comando `curl`:**
```bash
curl -s "http://localhost:8000/api/news-last-24h?user_id=2" | jq .
```

**Respuesta Esperada (`200 OK`):**
```json
[
  {
    "news_id": 5,
    "title": "Reunión del Centro de Estudiantes",
    "content": "Hoy a las 18hs se debate el nuevo plan de estudios.",
    "category_name": "Centro de Estudiantes",
    "created_at": "2026-06-27T22:19:52.690092"
  },
  {
    "news_id": 2,
    "title": "Resultados de los 31° Juegos",
    "content": "Resumen de las competencias realizadas esta tarde.",
    "category_name": "Deportes Universitarios",
    "created_at": "2026-06-27T20:49:52.690092"
  }
]
```

---

## 📘 Documentación Interactiva (Swagger / OpenAPI)

FastAPI genera automáticamente documentación interactiva accesible desde el navegador:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Schema (JSON):** `http://localhost:8000/openapi.json`
