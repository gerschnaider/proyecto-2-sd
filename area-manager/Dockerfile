FROM golang:alpine AS builder
WORKDIR /app

# Descargamos las dependencias
COPY go.mod go.sum ./
RUN go mod download

# Copiamos el código fuente y compilamos
COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o area-manager main.go

# Etapa 2: Imagen Final para Producción
FROM alpine:latest
WORKDIR /root/

# Traemos SOLO el binario compilado de la etapa anterior
COPY --from=builder /app/area-manager .

# Exponemos el puerto del microservicio
EXPOSE 8080

# Comando de arranque
CMD ["./area-manager"]