from fastapi import FastAPI, HTTPException, status
import psycopg2
import os

app = FastAPI(title="Servicio de Borrado de Noticias")

def get_db_connection():
    """Establece la conexión con la base de datos PostgreSQL."""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres")
        )
    except Exception as e:
        print(f"Error conectando a la BD: {e}")
        raise HTTPException(status_code=500, detail="Error interno de base de datos.")

@app.delete("/noticias/{news_id}")
def delete_news(news_id: int, user_id: int):
    """
    Elimina una noticia validando que el usuario solicitante sea el autor original.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        #Buscar la noticia para verificar su existencia y su dueño
        cur.execute("SELECT user_id FROM news WHERE news_id = %s AND is_deleted = FALSE;", (news_id,))
        result = cur.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="La noticia especificada no existe."
            )
            
        owner_id = result[0]
        
        #Verificar la regla de negocio: solo el creador puede borrarla 
        if owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Operación denegada. Solamente el cliente que envió la noticia puede borrarla."
            )
            
        #Si pasa la verificacion, borro la noticia (marcándola como eliminada)
        cur.execute("UPDATE news SET is_deleted = TRUE WHERE news_id = %s;", (news_id,))
        conn.commit()
        
        return {"status": "success", "message": f"Noticia {news_id} eliminada correctamente."}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()