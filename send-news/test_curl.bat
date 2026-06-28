@echo off
:: Script de prueba para send-news en Windows
title Probar Servicio Send-News (WebSocket)
chcp 65001 >nul

echo =====================================================================
echo           PRUEBA DEL SERVICIO SEND-NEWS (WebSocket)
echo =====================================================================
echo.
echo REQUISITOS: Python 3 con 'websockets' instalado
echo             (pip install websockets)
echo.

:: Solicitar la IP del nodo de Swarm (o localhost)
set /p "SWARM_IP=Ingrese la IP del nodo (o ENTER para 'localhost'): "
if "%SWARM_IP%"=="" set "SWARM_IP=localhost"

:: Solicitar user_id
set /p "USER_ID=Ingrese el user_id (o ENTER para '1'): "
if "%USER_ID%"=="" set "USER_ID=1"

:: Solicitar category_id
set /p "CATEGORY_ID=Ingrese el category_id (o ENTER para '2'): "
if "%CATEGORY_ID%"=="" set "CATEGORY_ID=2"

echo.
echo Conectando a ws://%SWARM_IP%:8765
echo Usuario: %USER_ID%  -  Categoria: %CATEGORY_ID%
echo Presione Ctrl+C para salir.
echo.

:: Ejecutar el cliente Python con los valores ingresados
python -c "import asyncio, websockets, json; URI='ws://%SWARM_IP%:8765'; UID=%USER_ID%; CID=%CATEGORY_ID%; exec(open('client_suscriptor.py').read().replace('ws://localhost:8765', URI).replace('user_id_prueba = 1', f'user_id_prueba = {UID}').replace('category_id_a_escuchar = 2', f'category_id_a_escuchar = {CID}'))" 2>nul

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo ejecutar. Verifique que:
    echo   - Python 3 esta instalado
    echo   - websockets esta instalado: pip install websockets
    echo   - El servicio esta corriendo en %SWARM_IP%:8765
)

echo.
echo =====================================================================
pause
