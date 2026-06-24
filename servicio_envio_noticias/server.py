import grpc
from concurrent import futures
import time
import logging
import queue
import threading

import noticias_pb2
# pyrefly: ignore [missing-import]
import noticias_pb2_grpc

class ServicioNoticiasServicer(noticias_pb2_grpc.ServicioNoticiasServicer):
    def __init__(self):
        # Diccionario para mapear: seccion -> lista_de_colas_de_clientes
        # Cada cliente conectado tendrá una cola donde se depositan las noticias a enviar
        self.suscriptores = {}  #acá guardo por ejemplo {1: [cola_juan, cola_pedro], 2: [cola_maria]}
        self.lock = threading.Lock() #por si dos personas intentan suscribirse al mismo ms

    def SuscribirASeccion(self, request, context):
        id_categoria = request.id_categoria
        cliente_id = request.cliente_id
        logging.info(f"Cliente {cliente_id} suscrito a la categoría ID: {id_categoria}")

        # Crear una cola para este cliente
        q = queue.Queue()

        with self.lock:
            if id_categoria not in self.suscriptores:
                self.suscriptores[id_categoria] = []
            self.suscriptores[id_categoria].append(q)

        try:
            # Mantener la conexión abierta y enviar noticias a medida que lleguen
            while context.is_active():
                try:
                    # Esperar por una noticia (timeout para poder chequear si el contexto sigue activo)
                    noticia = q.get(timeout=1)
                    yield noticia
                except queue.Empty:
                    continue
        except Exception as e:
            logging.error(f"Error con el cliente {cliente_id}: {e}")
        finally:
            # Cuando el cliente se desconecta, lo removemos de la lista
            with self.lock:
                if id_categoria in self.suscriptores and q in self.suscriptores[id_categoria]:
                    self.suscriptores[id_categoria].remove(q)
            logging.info(f"Cliente {cliente_id} desconectado de la categoría ID: {id_categoria}")

    def PublicarNoticia(self, request, context):
        id_categoria = request.id_categoria
        logging.info(f"Recibida nueva noticia para la categoría ID: {id_categoria} - Titulo: {request.titulo}")

        with self.lock:
            if id_categoria in self.suscriptores:
                # Enviar a todos los clientes suscritos a esta sección en esta réplica
                for q in self.suscriptores[id_categoria]:
                    q.put(request)

        return noticias_pb2.PublicacionResponse(exito=True, mensaje=f"Noticia enviada a los suscriptores locales de la categoría {id_categoria}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ServicioNoticiasServicer()
    noticias_pb2_grpc.add_ServicioNoticiasServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Servicio de Noticias (Pub/Sub via gRPC) escuchando en el puerto 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
