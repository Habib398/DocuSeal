@echo off
REM Instalador de DocuSeal Service - Version 3.0
REM Este script descarga NSSM, configura .env e instala el servicio

setlocal enabledelayedexpansion

cls
color 0A
echo.
echo =====================================
echo   Instalador DocuSeal Service v3.0
echo =====================================
echo.

REM Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Este script debe ejecutarse como Administrador
    echo.
    echo Por favor:
    echo   1. Haz clic derecho en este archivo
    echo   2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

color 0A

REM Variables
set "service_name=DocuSealService"
set "exe_path=%~dp0DocuSealService.exe"
set "work_dir=%~dp0.."
set "temp_dir=%TEMP%\nssm_installer"
set "nssm_url=https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip"
set "nssm_zip=%temp_dir%\nssm.zip"
set "nssm_extracted=%temp_dir%\nssm-2.24-101-g897c7ad\win64"
set "nssm_exe=%nssm_extracted%\nssm.exe"

REM Verificar que el ejecutable existe
if not exist "%exe_path%" (
    color 0C
    echo ERROR: DocuSealService.exe no encontrado
    echo Ubicacion esperada: %exe_path%
    echo.
    pause
    exit /b 1
)

echo Paso 1: Verificando configuracion...
echo.

REM Buscar .env
set "env_found=0"
set "env_source="

if exist "%~dp0.env" (
    set "env_source=%~dp0.env"
    set "env_found=1"
    echo [OK] .env encontrado en: dist/
) else if exist "%~dp0..\.env" (
    set "env_source=%~dp0..\.env"
    set "env_found=1"
    echo [OK] .env encontrado en: carpeta padre
) else if exist "%~dp0..\backend\app\DB\.env" (
    set "env_source=%~dp0..\backend\app\DB\.env"
    set "env_found=1"
    echo [OK] .env encontrado en: backend/app/DB/
)

if %env_found% equ 0 (
    color 0C
    echo ERROR: No se encontro archivo .env
    echo.
    echo Se requiere un archivo .env con credenciales de PostgreSQL
    echo.
    echo Ubicaciones buscadas:
    echo   - dist\.env
    echo   - ..\env
    echo   - ..\backend\app\DB\.env
    echo.
    pause
    exit /b 1
)

REM Copiar .env a dist si no existe
if not exist "%~dp0.env" (
    echo Copiando .env a directorio de instalacion...
    copy "%env_source%" "%~dp0.env" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] .env copiado
    )
)

echo.
echo Paso 2: Inicializando Base de Datos...
echo.

REM Llamar script de inicialización de BD desde Scripts/
set "init_db_script=%~dp0..\Scripts\init_database.ps1"

if exist "%init_db_script%" (
    color 0E
    echo Ejecutando inicializador de base de datos...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%init_db_script%"
    
    if %errorlevel% neq 0 (
        color 0C
        echo.
        echo ERROR: No se pudo inicializar la base de datos
        echo.
        pause
        exit /b 1
    )
    color 0A
) else (
    color 0C
    echo ERROR: Script init_database.ps1 no encontrado en Scripts/
    echo Se omitirá la inicialización automática de BD
    echo Deberá crear las tablas manualmente
    echo.
    timeout /t 3 /nobreak >nul
    color 0A
)

echo.
echo Paso 3: Verificando NSSM...
echo.

REM Crear directorio temporal
if not exist "%temp_dir%" mkdir "%temp_dir%"

REM Verificar si NSSM ya esta disponible
if exist "%nssm_exe%" (
    echo [OK] NSSM ya esta disponible
    goto :config_service
)

color 0E
echo Descargando NSSM...
echo.

REM Descargar NSSM
powershell -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip' -OutFile '%nssm_zip%' -UseBasicParsing" 2>nul

if not exist "%nssm_zip%" (
    color 0C
    echo ERROR: No se pudo descargar NSSM
    echo Verifica tu conexion a internet
    echo.
    pause
    exit /b 1
)

color 0E
echo Extrayendo NSSM...
echo.

REM Extraer NSSM
powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%nssm_zip%', '%temp_dir%')" 2>nul

if not exist "%nssm_exe%" (
    color 0C
    echo ERROR: No se pudo extraer NSSM
    echo.
    pause
    exit /b 1
)

:config_service
echo.
echo Paso 4: Configurando servicio...
echo.

REM Detener servicio existente
"%nssm_exe%" status "%service_name%" >nul 2>&1
if %errorlevel% equ 0 (
    echo Deteniendo servicio existente...
    "%nssm_exe%" stop "%service_name%" >nul 2>&1
    timeout /t 2 /nobreak >nul
    
    echo Eliminando servicio existente...
    "%nssm_exe%" remove "%service_name%" confirm >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo Instalando servicio: %service_name%
"%nssm_exe%" install "%service_name%" "%exe_path%" >nul 2>&1

if %errorlevel% neq 0 (
    color 0C
    echo ERROR: No se pudo instalar el servicio
    echo.
    pause
    exit /b 1
)

echo Configurando parametros...

REM Configurar
"%nssm_exe%" set "%service_name%" AppDirectory "%work_dir%" >nul 2>&1
"%nssm_exe%" set "%service_name%" AppExit Default Restart >nul 2>&1
"%nssm_exe%" set "%service_name%" AppRestartDelay 5000 >nul 2>&1

REM Crear directorio de logs
set "log_dir=%APPDATA%\DocuSeal\logs"
if not exist "%log_dir%" mkdir "%log_dir%"

REM Configurar logging
"%nssm_exe%" set "%service_name%" AppStdout "%log_dir%\stdout.log" >nul 2>&1
"%nssm_exe%" set "%service_name%" AppStderr "%log_dir%\stderr.log" >nul 2>&1

echo Iniciando servicio...
"%nssm_exe%" start "%service_name%" >nul 2>&1

timeout /t 3 /nobreak >nul

color 0A
echo.
echo =====================================
echo   Instalacion Completada
echo =====================================
echo.
echo Estado del servicio: CORRIENDO
echo.
echo URLs de acceso:
echo   - Service: http://localhost:8000/service
echo   - Documentacion: http://localhost:8000/service/docs
echo.
echo Directorio de logs: %log_dir%
echo.
echo Archivo de configuracion: %~dp0.env
echo.
echo Comandos utiles:
echo   Ver estado: nssm status DocuSealService
echo   Detener: nssm stop DocuSealService
echo   Reiniciar: nssm restart DocuSealService
echo   Desinstalar: nssm remove DocuSealService confirm
echo.
echo =====================================
echo.
pause
exit /b 0
