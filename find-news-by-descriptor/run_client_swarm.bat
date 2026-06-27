@echo off
:: Desactivar eco para que la consola se vea limpia
title Cliente de Busqueda HTTP - Docker Swarm

:: Verificar si existe el entorno virtual en la raiz del proyecto (carpeta padre) o local
if exist "..\.venv" (
    set "VENV_PATH=..\.venv"
) else if exist ".venv" (
    set "VENV_PATH=.venv"
) else (
    echo [ERROR] No se encontro la carpeta del entorno virtual venv ni en la raiz del proyecto ni en esta carpeta.
    echo Por favor, asegurate de que el entorno virtual este creado.
    pause
    exit /b 1
)

:: Solicitar la IP del nodo de Swarm (Manager o Worker) donde esta expuesto el puerto 8030
echo =====================================================================
echo           CLIENTE DE BUSQUEDA PARA DESPLIEGUE SWARM
echo =====================================================================
echo.
set /p "SWARM_IP=Ingrese la IP del nodo de Docker Swarm (o presione ENTER para 'localhost'): "

if "%SWARM_IP%"=="" (
    set "SWARM_IP=localhost"
)

:: El puerto expuesto por el servicio en Swarm es el 8030
set "SERVER_ADDRESS=http://%SWARM_IP%:8030"

echo.
echo Iniciando cliente de busqueda HTTP apuntando a: %SERVER_ADDRESS%
echo.

:: Ejecutar el cliente con la variable de entorno correspondiente
"%VENV_PATH%\Scripts\python.exe" "client.py"

pause
