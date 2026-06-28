# Comandos cURL para Find News Period

Estos son los comandos genéricos para interactuar con el microservicio `find-news-period`. 


### Buscar Noticias por Período
Este comando hace un `GET` para obtener todas las noticias creadas dentro de un rango de fechas específico. El sistema filtra automáticamente las noticias que fueron dadas de baja (soft delete).

```bash
curl -X GET "http://<ip>:<puerto>/api/news-period?fecha_inicio=<aaaa-mm-dd>&fecha_fin=<aaaa-mm-dd>"

```

### Ejemplo

```bash
curl -X GET "http://25.39.43.79:8000/api/news-period?fecha_inicio=2026-06-01&fecha_fin=2026-06-19""

```