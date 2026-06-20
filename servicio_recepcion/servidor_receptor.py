import grpc
from concurrent import futures
import noticias_pb2
import noticias_pb2_grpc

class ReceptorNoticiasServicer(noticias_pb2_grpc.ReceptorNoticiasServicer):
    
    def EnviarNoticia(self, request, context):
        print(f"\n[+] ¡Llegó una nueva noticia!")
        print(f"ID Noticia: {request.id_noticia}")
        print(f"Título: {request.titulo}")
        print(f"ID Autor: {request.autor_id}")
        print(f"Categoria: {request.id_categoria}")
        print(f"Contenido: {request.texto}")
        print(f"Fecha: {request.fecha}")
        
        # Pendiente: Conectar y guardar en la base de datos centralizada
        print("-> Guardando en la base de datos...")
        nuevo_id = None
        try:
            # Establecemos la conexión (traductor psycopg2)
            conexion = psycopg2.connect(
                host="localhost",       # Cambiará cuando se use la red de Docker Swarm
                database="noticias_db", # Nombre de la base de datos compartida
                user="postgres",        # Usuario por defecto de Postgres
                password="admin"        # Contraseña local de desarrollo
            )
            cursor = conexion.cursor()
            
            # Consulta SQL
            insert_query = """
                INSERT INTO news (title, user_id, category_id, content)
                VALUES (%s, %s, %s, %s)
                RETURNING news_id;
            """
            datos_a_insertar = (request.titulo, request.id_autor, request.id_categoria, request.texto)
            
            cursor.execute(insert_query, datos_a_insertar)
            nuevo_id = cursor.fetchone()[0] # Atrapamos el ID autoincremental (SERIAL) generado por Postgres
            
            conexion.commit()
            cursor.close()
            conexion.close()
            print(f"-> [ÉXITO] Noticia guardada correctamente con ID: {nuevo_id}")

        except Exception as e:
            print(f"-> [ERROR] No se pudo guardar en la base de datos. Detalle: {e}")
            # print("-> [MODO DESARROLLO] Generando un ID temporal para continuar la simulación...")
            # nuevo_id = 9999 # ID de respaldo para que el servicio de streaming no se quede sin dato
        

        # Pendiente: Hacer llamado gRPC al segundo servicio (Gonzalo_A)
        print("-> Avisando al servicio de distribución de noticias...")

        # Responder al cliente que todo salió bien
        return noticias_pb2.Respuesta(
            exito=True, 
            mensaje="La noticia fue recibida y guardada exitosamente."
        )

def serve():
    # Creamos el servidor gRPC con capacidad para 10 hilos concurrentes
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Vinculamos los trabajadores al servidor
    noticias_pb2_grpc.add_ReceptorNoticiasServicer_to_server(ReceptorNoticiasServicer(), servidor)
    
    # Lo ponemos a escuchar en el puerto 50051 (Estandar para gRPC)
    puerto = '50051'
    servidor.add_insecure_port(f'[::]:{puerto}')
    print(f"Servidor de Recepción de Noticias encendido y escuchando en el puerto {puerto}...")
    
    servidor.start()
    servidor.wait_for_termination()

if __name__ == '__main__':
    serve()