import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
from datetime import date

load_dotenv()

app = FastAPI(
    title="Servicio de Búsqueda por Período",
    description="Devuelve noticias ocurridas en un rango de fechas."
)


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
        raise HTTPException(status_code=500, detail=f"Error conectando a BD: {e}")


@app.get("/api/news-period")
def get_news_by_period(fecha_inicio: date, fecha_fin: date):
    """Devuelve noticias entre dos fechas (YYYY-MM-DD).

    FastAPI validará y convertirá automáticamente los parámetros a objetos `date`.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT n.title, n.content, a.name AS category_name, n.created_at
                FROM news n
                JOIN areas a ON n.category_id = a.category_id
                WHERE n.is_deleted = FALSE
                AND a.is_deleted = FALSE
                AND n.created_at::date BETWEEN %s AND %s
                ORDER BY n.created_at DESC
            """
            cur.execute(query, (fecha_inicio, fecha_fin))
            rows = cur.fetchall()
            return jsonable_encoder(rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}