# Comandos cURL para el servicio Get News Load By Area

Estos son los comandos genéricos para interactuar con el microservicio `get-news-load-by-area`.

### 1. Obtener la carga de noticias
Este comando hace un `GET` para obtener la cantidad de noticias registradas agrupadas por cada área (categoría). Muestra el ID de la categoría, el nombre y el conteo de noticias activas.

```bash
curl -X GET http://<ip>:<puerto>/api/news-load
```
*(Si lo pruebas de forma local con Docker Compose o Swarm en tu máquina, el puerto expuesto suele ser el `8003`, por ejemplo: `http://localhost:8003/api/news-load`)*

### 2. Verificar estado de salud (Health Check)
Este comando hace un `GET` al endpoint de salud. Sirve para que Docker o el balanceador de carga puedan comprobar rápidamente si el contenedor está vivo y respondiendo peticiones.

```bash
curl -X GET http://<ip>:<puerto>/health
```
