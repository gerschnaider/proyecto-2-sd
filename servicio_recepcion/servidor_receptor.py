from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import grpc
import uvicorn

# Importamos los archivos gRPC SOLO para hablar con Gonzalo
import noticias_pb2
import noticias_pb2_grpc

app = FastAPI(title="Microservicio de Recepción", description="API Gateway para periodistas")

class NuevaNoticia(BaseModel):
    titulo: str
    id_autor: int
    id_categoria: int
    texto: str

# Creamos el endpoint
@app.post("/api/noticias")
def recibir_noticia(noticia: NuevaNoticia):
    print(f"Recibiendo nueva noticia: {noticia.titulo}")
    
    try:
        conexion = psycopg2.connect(
            host="db", 
            database="noticias_db",
            user="postgres",
            password="admin"
        )
        cursor = conexion.cursor()

        consulta_sql = """
            INSERT INTO news (title, user_id, category_id, content)
            VALUES (%s, %s, %s, %s)
            RETURNING news_id; 
        """
        
        cursor.execute(consulta_sql, (noticia.titulo, noticia.id_autor, noticia.id_categoria, noticia.texto))
        nuevo_id = cursor.fetchone()[0]

        conexion.commit()
        cursor.close()
        conexion.close()
        
        print(f"[ÉXITO DB] Noticia guardada en la base de datos con ID: {nuevo_id}")
        
        print("Avisando al servicio de distribución de noticias...")
        try:
            with grpc.insecure_channel('servicio_noticias:50051') as canal_gonza:
                stub_gonza = noticias_pb2_grpc.ServicioNoticiasStub(canal_gonza)
                
                # Armamos el paquete gRPC con los datos que llegaron del JSON
                noticia_a_repartir = noticias_pb2.Noticia(
                    id_noticia=nuevo_id,
                    titulo=noticia.titulo,
                    id_autor=noticia.id_autor,
                    id_categoria=noticia.id_categoria,
                    texto=noticia.texto,
                    fecha="" 
                )
                
                respuesta_gonza = stub_gonza.PublicarNoticia(noticia_a_repartir)
                print(f"[ÉXITO DISTRIBUCIÓN] {respuesta_gonza.mensaje}")
                
        except Exception as error_distribucion:
            print(f"[AVISO] La noticia se guardó, pero falló la distribución: {error_distribucion}")

        # Le respondemos al cliente
        return {
            "exito": True, 
            "mensaje": "Noticia recibida y procesada correctamente",
            "id_generado": nuevo_id
        }

    except Exception as e:
        print(f"[ERROR GENERAL] {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# El motor que enciende el servidor
if __name__ == '__main__':
    print("Iniciando API Gateway en el puerto 50050...")
    uvicorn.run(app, host="0.0.0.0", port=50050)