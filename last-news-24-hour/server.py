import os
from datetime import date, timedelta
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import psycopg2
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Query
# pyrefly: ignore [missing-import]
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
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "secreta"),
            dbname=os.getenv("DB_NAME", "sistema_db")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a la base de datos: {e}")


def get_user_subscribed_categories(user_id: int):
    """Obtiene el conjunto de nombres de categorías a las que un usuario está suscripto."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT a.name
                FROM areas a
                JOIN subscriptions s ON a.category_id = s.category_id
                WHERE s.user_id = %s AND a.is_deleted = FALSE;
            """
            cur.execute(query, (user_id,))
            rows = cur.fetchall()
            return {row[0] for row in rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando suscripciones: {e}")
    finally:
        conn.close()


def get_news_last_24(user_id: Optional[int] = None):
    """Consulta directa a PostgreSQL como respaldo."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if user_id is not None:
                query = """
                    SELECT
                        n.news_id,
                        n.title,
                        n.content,
                        a.name AS category_name,
                        n.created_at
                    FROM news n
                    JOIN areas a ON n.category_id = a.category_id
                    JOIN subscriptions s ON n.category_id = s.category_id
                    WHERE n.created_at >= NOW() - INTERVAL '24 hours'
                      AND n.is_deleted = FALSE
                      AND a.is_deleted = FALSE
                      AND s.user_id = %s
                    ORDER BY n.created_at DESC;
                """
                cur.execute(query, (user_id,))
            else:
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
                      AND n.is_deleted = FALSE
                      AND a.is_deleted = FALSE
                    ORDER BY n.created_at DESC;
                """
                cur.execute(query)
            rows = cur.fetchall()
            return jsonable_encoder(rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando la base de datos: {e}")
    finally:
        conn.close()


def get_news_from_find_news_period(user_id: Optional[int] = None):
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
            news_list = json.loads(payload)
            if user_id is not None:
                subscribed_categories = get_user_subscribed_categories(user_id)
                news_list = [n for n in news_list if n.get("category_name") in subscribed_categories]
            return news_list
    except (HTTPError, URLError, TimeoutError, ValueError):
        # Si falla el microservicio, se hace la consulta directa a la base de datos
        return get_news_last_24(user_id)


@app.get("/api/news-last-24h")
def get_news_last_24h(user_id: Optional[int] = Query(None, description="ID del usuario para filtrar por sus suscripciones")):
    """Devuelve las noticias de las últimas 24 horas, opcionalmente filtradas por las suscripciones del usuario."""
    return get_news_from_find_news_period(user_id)


@app.get("/health")
def health_check():
    return {"status": "ok"}

