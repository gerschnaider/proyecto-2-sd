import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.errors import UniqueViolation, ForeignKeyViolation

app = FastAPI(title="Servicio de Suscripciones (Directo a BD)")

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sistema_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secreta")

# --- MODELOS PYDANTIC ---
class SuscripcionRequest(BaseModel):
    user_id: int
    category_id: int

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        return conn
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error conectando a la BD: {str(e)}"
        )

# GESTIÓN DE SUSCRIPCIONES
@app.post("/suscribir")
def suscribir_cliente(suscripcion: SuscripcionRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # VALIDAR SI EL ÁREA EXISTE Y SI NO ESTÁ ELIMINADA LÓGICAMENTE
        cur.execute("SELECT name, is_deleted FROM areas WHERE category_id = %s;", (suscripcion.category_id,))
        area_encontrada = cur.fetchone()
        
        if not area_encontrada:
            raise HTTPException(
                status_code=400,
                detail=f"El área {suscripcion.category_id} no existe en la base de datos."
            )
            
        nombre_del_area = area_encontrada[0] 
        area_eliminada = area_encontrada[1] 

        # CHEQUEO DEL BOOLEANO
        if area_eliminada:
            raise HTTPException(
                status_code=400,
                detail=f"El área '{nombre_del_area}' ha sido dada de baja y no acepta nuevas suscripciones."
            )

        # INTENTAR LA SUSCRIPCIÓN
        cur.execute(
            "INSERT INTO subscriptions (user_id, category_id) VALUES (%s, %s);",
            (suscripcion.user_id, suscripcion.category_id),
        )
        
        conn.commit()
        return {
            "mensaje": f"Usuario {suscripcion.user_id} suscrito a '{nombre_del_area}'.",
            "success": True
        }
        
    except UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=400, detail="El usuario ya está suscrito a esta área."
        )
    except ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(
            status_code=400, detail="El usuario especificado no existe en la base de datos."
        )
    except Exception as e:
        conn.rollback()
        
        # para que no tape el HTTPException de área no encontrada
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        cur.close()
        conn.close()


# ENDPOINT PARA DESUSCRIBIRSE DE UN ÁREA
@app.delete("/desuscribir")
def desuscribir_cliente(suscripcion: SuscripcionRequest):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # validar que exista el area en la base de datos (incluso si está en is_deleted = True)
        cur.execute(
            "SELECT name FROM areas WHERE category_id = %s;",
            (suscripcion.category_id,)
        )
        area_encontrada = cur.fetchone()

        if not area_encontrada:
            raise HTTPException(
                status_code=400,
                detail=f"El área {suscripcion.category_id} no existe en la base de datos."
            )

        nombre_del_area = area_encontrada[0]

        # validar que el usuario exista
        cur.execute(
            "SELECT 1 FROM users WHERE user_id = %s;",
            (suscripcion.user_id,)
        )

        if not cur.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El usuario especificado no existe en la base de datos."
            )

        # intenta eliminar la suscripción
        cur.execute(
            "DELETE FROM subscriptions WHERE user_id = %s AND category_id = %s;",
            (suscripcion.user_id, suscripcion.category_id),
        )

        filas_afectadas = cur.rowcount

        if filas_afectadas == 0:
            raise HTTPException(
                status_code=404,
                detail="El usuario no está suscrito a esta área."
            )

        conn.commit()

        return {
            "mensaje": f"Usuario {suscripcion.user_id} dado de baja del área '{nombre_del_area}'.",
            "success": True
        }

    except Exception as e:
        conn.rollback()

        # Para que no tape los HTTPException
        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )

    finally:
        cur.close()
        conn.close()