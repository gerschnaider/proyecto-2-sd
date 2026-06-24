import sys
import os
import grpc

# Agregamos la raíz del proyecto al path de Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from protos import news_search_pb2
from protos import news_search_pb2_grpc

def run():
    # Nos conectamos al puerto local del servidor gRPC
    server_address = os.environ.get("SERVER_ADDRESS", "localhost:50051")
    print(f"Estableciendo canal de comunicación con {server_address}...")
    
    # Creamos un canal inseguro (sin encriptación SSL, para desarrollo local)
    with grpc.insecure_channel(server_address) as channel:
        # El stub es el objeto que nos permite llamar a las funciones del servidor
        stub = news_search_pb2_grpc.NewsSearchServiceStub(channel)
        
        print("Escribe 'salir' para terminar el cliente.")
        
        while True:
            # Le pedimos al usuario que escriba un término a buscar en la consola
            descriptor = input("\nIngrese la palabra clave o descriptor a buscar (mínimo 3 caracteres): ")
            
            if descriptor.strip().lower() in ['salir', 'exit', 'quit']:
                print("Cerrando cliente de prueba...")
                break
                
            if len(descriptor.strip()) < 3:
                print("⚠️ Error: Por favor, ingresa al menos 3 caracteres para que la búsqueda sea efectiva.")
                print('\n\n\n')
                continue
                
            try:
                # Instanciamos la petición con el descriptor ingresado
                request = news_search_pb2.SearchRequest(descriptor=descriptor)
                
                # Hacemos la llamada RPC (Request-Reply sincrónico)
                print("Enviando petición de búsqueda...")
                response = stub.SearchByDescriptor(request)
                
                # Mostramos los resultados devueltos por el servidor
                print("\n==============================================")
                print(f"  RESULTADOS ENCONTRADOS ({len(response.news)})")
                print("==============================================")
                
                if not response.news:
                    print("No se encontraron noticias que coincidan con ese descriptor.")
                    print('\n\n\n')
                else:
                    for idx, item in enumerate(response.news, 1):
                        print(f"\n[{idx}] Título: {item.title}")
                        print(f"    Noticia ID: {item.news_id} | Categoría ID: {item.category_id} | Creador ID: {item.user_id}")
                        print(f"    Fecha de creación: {item.created_at}")
                        print(f"    Contenido: {item.content}")
                        print("-" * 46)

                    print('\n==================================================================================\n\n\n')
                
            except grpc.RpcError as e:
                # Captura excepciones específicas enviadas desde el Servidor gRPC
                print(f"\n❌ Error de gRPC ({e.code().name}): {e.details()}")

if __name__ == '__main__':
    run()
