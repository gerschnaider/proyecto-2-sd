# Swarm Commands

## Salvedad inicial

La primera vez, antes de hacer `docker stack deploy`, hay que construir las imagenes con `docker build` porque Swarm no ejecuta el build del compose.

## Iniciar Swarm

```bash
docker swarm init --advertise-addr <IP_DEL_MANAGER>
```

## Conectarse al Swarm

```bash
docker swarm join --token <TOKEN> <IP_DEL_MANAGER>:2377
```

## Salir del Swarm

```bash
docker swarm leave --force
```

## Desplegar el stack

```bash
docker stack deploy -c docker-compose.yml consorcio
```

## Ver stacks activos

```bash
docker stack ls
```

## Ver servicios del stack

```bash
docker stack services consorcio
```

## Ver tareas/containers del stack

```bash
docker stack ps consorcio
```

## Ver contenedores corriendo

```bash
docker ps
```

## Ver logs de un servicio

```bash
docker service logs -f consorcio_<nombre_servicio>
```

## Ver logs de un contenedor puntual

```bash
docker logs -f <container_id_o_nombre>
```

## Ver actividad del Swarm

```bash
docker service ps consorcio_<nombre_servicio>
```

## Bajar el stack

```bash
docker stack rm consorcio
```
