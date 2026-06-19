import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()

app = FastAPI(
    title="Servicio de Carga de Noticias por Área",
    description="Microservicio que devuelve la cantidad de noticias por cada área registrada.",
    version="1.0.0"
)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            dbname=os.getenv("DB_NAME", "postgres")
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a la base de datos: {e}")

@app.get("/api/news-load")
def get_news_load():
    """
    Obtiene la carga (cantidad) de noticias en cada una de las áreas.
    Incluye áreas con 0 noticias.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Query para contar las noticias agrupadas por categoría
            # Se usa LEFT JOIN para incluir áreas sin noticias
            query = """
                SELECT 
                    a.category_id, 
                    a.name AS category_name, 
                    COUNT(n.news_id) AS news_count
                FROM 
                    areas a
                LEFT JOIN 
                    news n ON a.category_id = n.category_id
                GROUP BY 
                    a.category_id, a.name
                ORDER BY 
                    a.category_id ASC;
            """
            cur.execute(query)
            results = cur.fetchall()
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando la base de datos: {e}")
    finally:
        conn.close()

@app.get("/health")
def health_check():
    """
    Endpoint para que el balanceador (proxy reverso) o Docker Swarm verifiquen 
    el estado del contenedor.
    """
    return {"status": "ok"}
