import os
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from psycopg2.extras import RealDictCursor
import json

load_dotenv()

app = FastAPI(
    title="Servicio de Noticias de las Últimas 24 Horas",
    description="Devuelve las noticias publicadas en las últimas 24 horas."
)


def get_find_news_period_url():
    return os.getenv("FIND_NEWS_PERIOD_URL", "http://find-news-service:8000/api/news-period")


def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASSWORD", "password"),
            dbname=os.getenv("DB_NAME", "noticias_db")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a la base de datos: {e}")


def get_news_last_24():
    """Consulta directa a PostgreSQL como respaldo."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT
                    n.news_id,
                    n.title,
                    n.content,
                    a.name AS category_name,
                    n.created_at
                FROM news n
                JOIN areas a ON n.category_id = a.category_id
                WHERE n.created_at >= NOW() - INTERVAL '24 hours'
                ORDER BY n.created_at DESC;
            """
            cur.execute(query)
            rows = cur.fetchall()
            return jsonable_encoder(rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando la base de datos: {e}")
    finally:
        conn.close()


def get_news_from_find_news_period():
    """Primera opción: consultar al microservicio find_news_period."""
    today = date.today()
    yesterday = today - timedelta(days=1)

    query_params = urlencode({
        "fecha_inicio": yesterday.isoformat(),
        "fecha_fin": today.isoformat()
    })
    url = f"{get_find_news_period_url()}?{query_params}"

    try:
        with urlopen(url, timeout=5) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except (HTTPError, URLError, TimeoutError, ValueError):
        "Si falla el microservicio, se hace la consulta directa a la base de datos"
        return get_news_last_24()


@app.get("/api/news-last-24h")
def get_news_last_24h():
    """Devuelve las noticias de las últimas 24 horas consultando primero el microservicio de período."""
    print("Consultando microservicio find_news_period...")
    return get_news_from_find_news_period()


@app.get("/health")
def health_check():
    return {"status": "ok"}
