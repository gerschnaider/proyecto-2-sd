@echo off
:: Desactivar eco para que la consola se vea limpia
title Probar Microservicio con Curl

echo =====================================================================
echo           PRUEBA RAPIDA DEL SERVICIO CON CURL
echo =====================================================================
echo.

:: Solicitar la IP del nodo de Swarm (o localhost)
set /p "SWARM_IP=Ingrese la IP del nodo (o presione ENTER para 'localhost'): "

if "%SWARM_IP%"=="" (
    set "SWARM_IP=localhost"
)

:: Solicitar el descriptor a buscar
set /p "DESCRIPTOR=Ingrese el descriptor a buscar (ej: economia, deporte, etc): "

if "%DESCRIPTOR%"=="" (
    set "DESCRIPTOR=test"
)

echo.
echo Realizando peticion HTTP GET con Curl...
echo URL: http://%SWARM_IP%:8030/api/news-descriptor?descriptor=%DESCRIPTOR%
echo.

:: Ejecutar curl con formato JSON formateado si esta disponible, o plano
curl -X GET "http://%SWARM_IP%:8030/api/news-descriptor?descriptor=%DESCRIPTOR%"

echo.
echo.
echo =====================================================================
pause
