import sys
import os
from concurrent import futures
import grpc

# Agregamos la raíz del proyecto al path de Python
# Esto garantiza que 'import protos' funcione correctamente desde cualquier lugar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protos import news_search_pb2
from protos import news_search_pb2_grpc
from src.db import search_news_by_descriptor

class NewsSearchServicer(news_search_pb2_grpc.NewsSearchServiceServicer):
    """
    Clase que hereda del Servicer autogenerado por gRPC.
    Aquí implementamos la lógica real de las funciones declaradas en el .proto
    """
    
    def SearchByDescriptor(self, request, context):
        print(f"[gRPC] Petición recibida para buscar descriptor: '{request.descriptor}'")
        
        # 1. Validación básica de entrada
        if not request.descriptor.strip():
            print("[gRPC] Intento de búsqueda con descriptor vacío.")
            # Definimos un código de error de gRPC estándar
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("El descriptor no puede estar vacío.")
            return news_search_pb2.SearchResponse()
            
        try:
            # 2. Consultamos la base de datos de manera segura (con db.py)
            db_results = search_news_by_descriptor(request.descriptor)
            
            # 3. Construimos el mensaje de respuesta de gRPC
            response = news_search_pb2.SearchResponse()
            
            for row in db_results:
                # Mapeamos cada diccionario devuelto por Postgres a un NewsItem
                news_item = news_search_pb2.NewsItem(
                    news_id=row['news_id'],
                    title=row['title'],
                    user_id=row['user_id'],
                    category_id=row['category_id'],
                    content=row['content'],
                    created_at=str(row['created_at'])  # Convertimos la fecha (datetime) a texto
                )
                # Agregamos la noticia mapeada a la lista repetida (repeated)
                response.news.append(news_item)
                
            print(f"[gRPC] Éxito. Retornando {len(response.news)} resultados.")
            return response
            
        except Exception as e:
            print(f"[gRPC] Error al procesar la búsqueda: {e}")
            # En caso de fallas de base de datos u otros, retornamos error interno
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno en el microservicio: {str(e)}")
            return news_search_pb2.SearchResponse()

def serve():
    # Creamos un servidor gRPC.
    # Usamos ThreadPoolExecutor para que pueda atender múltiples peticiones concurrentes en hilos
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Registramos nuestra implementación en el servidor
    news_search_pb2_grpc.add_NewsSearchServiceServicer_to_server(NewsSearchServicer(), server)
    
    # Escuchamos en todas las IPs locales [::] en el puerto configurado o el 50051 por defecto
    port = os.environ.get("SERVER_PORT", "50051")
    server.add_insecure_port(f'[::]:{port}')
    
    print(f"Servidor gRPC iniciado. Escuchando en el puerto {port}...")
    server.start()
    
    # Mantiene el servidor activo indefinidamente sin bloquear el hilo principal
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
