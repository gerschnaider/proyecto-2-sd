import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Servicio de Suscripciones (Directo a BD)")

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "noticias_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgrespassword")

# --- MODELOS PYDANTIC ---
class SuscripcionRequest(BaseModel):
    user_id: int
    category_id: int

class NuevaArea(BaseModel):
    category_id: int
    name: str

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error conectando a la BD: {str(e)}"
        )

# ==========================================
# 1. GESTIÓN DE ÁREAS (AHORA DIRECTO A LA BD)
# ==========================================
@app.post("/areas")
def agregar_area(area: NuevaArea):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO areas (category_id, name) VALUES (%s, %s);",
            (area.category_id, area.name)
        )
        conn.commit()
        return {"mensaje": f"Área '{area.name}' agregada a la base de datos."}
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="El ID del área ya existe en la BD.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/areas")
def listar_areas():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT category_id, name FROM areas ORDER BY category_id;")
    filas = cur.fetchall()
    cur.close()
    conn.close()
    return filas

# ==========================================
# 2. GESTIÓN DE SUSCRIPCIONES
# ==========================================
@app.post("/suscribir")
def suscribir_cliente(suscripcion: SuscripcionRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. VALIDAR SI EL ÁREA EXISTE EN LA BASE DE DATOS
        cur.execute("SELECT name FROM areas WHERE category_id = %s;", (suscripcion.category_id,))
        area_encontrada = cur.fetchone()
        
        if not area_encontrada:
            raise HTTPException(
                status_code=400,
                detail=f"El área {suscripcion.category_id} no existe en la base de datos."
            )
            
        nombre_del_area = area_encontrada[0] # Al no usar RealDictCursor acá, es una tupla

        # 2. VERIFICAR SI EL USER_ID EXISTE (Si no, lo creamos)
        cur.execute("SELECT user_id FROM users WHERE user_id = %s;", (suscripcion.user_id,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO users (user_id, name) VALUES (%s, %s);",
                (suscripcion.user_id, f"Auto-generated User {suscripcion.user_id}")
            )

        # 3. INTENTAR LA SUSCRIPCIÓN
        cur.execute(
            "INSERT INTO subscriptions (user_id, category_id) VALUES (%s, %s);",
            (suscripcion.user_id, suscripcion.category_id),
        )
        
        conn.commit()
        return {
            "mensaje": f"Usuario {suscripcion.user_id} suscrito a '{nombre_del_area}'.",
            "success": True
        }
        
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=400, detail="El usuario ya está suscrito a esta área."
        )
    except Exception as e:
        conn.rollback()
        # Para que no tape el HTTPException de área no encontrada
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.delete("/desuscribir")
def desuscribir_cliente(suscripcion: SuscripcionRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM subscriptions WHERE user_id = %s AND category_id = %s;",
            (suscripcion.user_id, suscripcion.category_id),
        )
        filas_afectadas = cur.rowcount
        conn.commit()

        if filas_afectadas == 0:
            raise HTTPException(status_code=404, detail="La suscripción no existe.")

        return {
            "mensaje": f"Usuario {suscripcion.user_id} dado de baja del área {suscripcion.category_id}."
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/suscripciones/{user_id}")
def obtener_suscripciones(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # MAGIA SQL: Usamos un JOIN para cruzar las tablas de suscripciones y áreas
        query = """
            SELECT s.category_id, a.name 
            FROM subscriptions s
            JOIN areas a ON s.category_id = a.category_id
            WHERE s.user_id = %s;
        """
        cur.execute(query, (user_id,))
        filas = cur.fetchall()
        
        return {"user_id": user_id, "suscripciones": filas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()