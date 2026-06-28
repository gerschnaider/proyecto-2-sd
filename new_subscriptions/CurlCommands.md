# Comandos cURL para el Area De Nuevas Subscripciones

Estos son los comandos genéricos para interactuar con el microservicio `new-subscriptions`. 


### 1. Inscribir un cliente a un área existente
Este comando hace un `POST` para registrar un cliente a una determinada área en la base de datos. Requiere enviar el ID del cliente y la ID del área.

```bash
curl -X POST http://<ip>:<puerto>/suscribir \
  -H "Content-Type: application/json" \
  -d '{"user_id": <id_del_usuario>, "category_id": <id_del_area>}'
```
*Ejemplo:* `{"user_id": 42, "category_id": 1}`

### 2. Desubscribir un cliente
Este comando hace un `DELETE` de la fila referida al cliente y área seleccionada. Requiere enviar en el body el ID del Cliente y la ID del área a desuscribir.

```bash
curl -X DELETE http://<ip>:<puerto>/desuscribir \
  -H "Content-Type: application/json" \
  -d '{"user_id": <id_del_usuario>, "category_id": <id_del_area>}'
```

*Ejemplo:* `{"user_id": 42, "category_id": 1}`
