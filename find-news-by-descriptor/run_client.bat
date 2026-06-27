@echo off
:: Desactivar eco para que la consola se vea limpia
title Cliente de Busqueda gRPC

:: Verificar si existe el entorno virtual
if not exist ".venv" (
    echo [ERROR] No se encontro la carpeta del entorno virtual (.venv^).
    echo Por favor, asegurate de que el entorno virtual este creado en la raiz del proyecto.
    pause
    exit /b 1
)

echo Iniciando cliente de busqueda gRPC...
:: Ejecutamos python directamente desde el entorno virtual pasando la ruta del script.
:: Esto hace que use todas las librerias instaladas (grpc, protobuf) sin tener que activar el venv en la terminal.
".venv\Scripts\python.exe" "news_search\client.py"

pause
