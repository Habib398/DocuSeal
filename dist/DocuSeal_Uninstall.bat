@echo off
REM Desinstalador de DocuSeal Service
REM Este script desinstala el servicio de Windows

setlocal enabledelayedexpansion

cls
color 0A
echo.
echo =====================================
echo   Desinstalador DocuSeal Service
echo =====================================
echo.

REM Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Este script debe ejecutarse como Administrador
    echo.
    pause
    exit /b 1
)

set "service_name=DocuSealService"
set "temp_dir=%temp%\nssm_installer"
set "nssm_exe=%temp_dir%\nssm-2.24-101-g897c7ad\win64\nssm.exe"

REM Verificar si el servicio existe
"%nssm_exe%" status "%service_name%" >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo El servicio '%service_name%' no está instalado
    echo.
    pause
    exit /b 0
)

REM Confirmar desinstalación
color 0E
echo ¿Deseas desinstalar el servicio '%service_name%'?
echo.
echo Escribe S para confirmar (o cualquier otra tecla para cancelar):
set /p confirm=

if /i not "%confirm%"=="S" (
    color 0E
    echo Operación cancelada
    echo.
    pause
    exit /b 0
)

color 0A
echo Deteniendo el servicio...
"%nssm_exe%" stop "%service_name%" >nul 2>&1
timeout /t 2 /nobreak >nul

color 0A
echo Desinstalando el servicio...
"%nssm_exe%" remove "%service_name%" confirm >nul 2>&1

if %errorlevel% equ 0 (
    color 0A
    echo.
    echo =====================================
    echo   Desinstalación Completada
    echo =====================================
    echo.
    echo El servicio '%service_name%' ha sido desinstalado correctamente.
    echo.
) else (
    color 0C
    echo.
    echo =====================================
    echo   Error en la Desinstalación
    echo =====================================
    echo.
    echo Hubo un error al desinstalar el servicio.
    echo Intenta desde Servicios de Windows (services.msc)
    echo.
)

pause
exit /b %errorlevel%
