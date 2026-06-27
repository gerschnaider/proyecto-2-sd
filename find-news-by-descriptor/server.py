import os
import psycopg2
from psycopg2.extras import RealDictCursor
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.encoders import jsonable_encoder
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Servicio de Búsqueda por Descriptor",
    description="Devuelve noticias cuyo título o contenido coincida con el descriptor provisto."
)

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
        raise HTTPException(status_code=500, detail=f"Error conectando a BD: {e}")

@app.get("/api/news-descriptor")
def get_news_by_descriptor(descriptor: str):
    """
    Busca noticias cuyo título o contenido coincida con el descriptor provisto.
    Utiliza consultas parametrizadas para evitar ataques de Inyección SQL.
    """
    if not descriptor.strip():
        raise HTTPException(status_code=400, detail="El descriptor no puede estar vacío.")

    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Consulta SQL parametrizada con %s original
            query = """
                SELECT n.news_id, n.title, n.user_id, n.category_id, n.content, n.created_at
                FROM news n
                LEFT JOIN areas a ON n.category_id = a.category_id
                WHERE n.is_deleted = FALSE
                      AND to_tsvector('spanish', n.title || ' ' || n.content || ' ' || COALESCE(a.name, '')) 
                      @@ plainto_tsquery('spanish', %s)
                ORDER BY n.created_at DESC;
            """
            cur.execute(query, (descriptor.strip(),))
            rows = cur.fetchall()
            return jsonable_encoder(rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}
