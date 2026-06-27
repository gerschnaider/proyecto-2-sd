# Comandos cURL para el Area Manager

Estos son los comandos genéricos para interactuar con el microservicio `area-manager`. 


### 1. Crear un Área
Este comando hace un `POST` para registrar una nueva área en la base de datos. Requiere enviar el nombre del área y el ID del usuario creador.

```bash
curl -X POST http://<ip>:<puerto>/areas \
  -H "Content-Type: application/json" \
  -d '{"name": "<nombre_del_area>", "user_id": <id_del_usuario>}'
```
*Ejemplo:* `{"name": "Inteligencia Artificial", "user_id": 1}`

### 2. Borrar un Área (y sus noticias en cascada)
Este comando hace un `DELETE` apuntando al nombre del área directamente en la URL. También requiere que mandes en el body el `user_id` del dueño original para verificar permisos.

```bash
curl -X DELETE "http://<ip>:<puerto>/areas/<nombre_del_area_url_encoded>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": <id_del_usuario>}'
```

*(Tip: si el nombre de tu área tiene espacios, tenés que reemplazar los espacios por `%20` en la URL. Es decir, si el área es "Data Science", la URL debe ser `http://localhost:8080/areas/Data%20Science`).*
