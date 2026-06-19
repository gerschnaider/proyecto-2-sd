import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    Establece una conexión con la base de datos PostgreSQL utilizando
    variables de entorno. Si no están configuradas, utiliza valores por defecto.
    """
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres")
    )

def search_news_by_descriptor(descriptor: str):
    """
    Busca noticias cuyo título o contenido coincida con el descriptor provisto.
    Utiliza consultas parametrizadas para evitar ataques de Inyección SQL.
    """
    conn = get_db_connection()
    try:
        # Usamos RealDictCursor para que los resultados vengan como diccionarios
        # en lugar de tuplas, lo cual facilita mapear los datos a gRPC
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Consulta SQL parametrizada con %s
            # Hacemos un JOIN con la tabla areas para poder buscar también por el nombre de la categoría
            query = """
                SELECT n.news_id, n.title, n.user_id, n.category_id, n.content, n.created_at
                FROM news n
                LEFT JOIN areas a ON n.category_id = a.category_id
                WHERE n.title ILIKE %s OR n.content ILIKE %s OR a.name ILIKE %s
                ORDER BY n.created_at DESC;
            """
            
            # Preparamos el patrón de búsqueda (ej. "%deportes%")
            search_pattern = f"%{descriptor}%"
            
            # Ejecutamos pasando los parámetros en una tupla (tres veces porque hay tres %s)
            # Psycopg2 se encarga de escapar y sanitizar los inputs de forma segura.
            cur.execute(query, (search_pattern, search_pattern, search_pattern))
            
            # Traemos todas las filas coincidentes
            rows = cur.fetchall()
            return rows
    except Exception as e:
        print(f"Error al buscar noticias en la base de datos: {e}")
        raise e
    finally:
        conn.close()
