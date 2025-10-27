# Script de Instalación de Dependencias - DocuSeal
# Compatible con Windows 10/11 y Windows Server 2016/2019/2022

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DocuSeal - Instalador de Dependencias" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en la raíz del proyecto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

Write-Host "Directorio del proyecto: $projectRoot" -ForegroundColor Yellow
Write-Host ""

# Función para verificar si un comando existe
function Test-Command {
    param($command)
    try {
        if (Get-Command $command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Verificar Python
Write-Host "[1/4] Verificando Python..." -ForegroundColor Green
if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor, instala Python 3.8 o superior desde https://www.python.org" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version
Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green

# Verificar Node.js
Write-Host "[2/4] Verificando Node.js..." -ForegroundColor Green
if (-not (Test-Command "node")) {
    Write-Host "ERROR: Node.js no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor, instala Node.js 16.x o superior desde https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

$nodeVersion = node --version
Write-Host "Node.js encontrado: $nodeVersion" -ForegroundColor Green
Write-Host ""

# Instalar dependencias del Backend (Python)
Write-Host "[3/4] Instalando dependencias del Backend (Python)..." -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray

# Crear entorno virtual si no existe
if (-not (Test-Path "venv")) {
    Write-Host "Creando entorno virtual de Python..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        exit 1
    }
    Write-Host "Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "Entorno virtual ya existe" -ForegroundColor Green
}

# Activar entorno virtual e instalar dependencias
Write-Host "Instalando paquetes de Python..." -ForegroundColor Yellow

# Usar el python del entorno virtual directamente (evita problemas de activación)
$venvPython = ".\venv\Scripts\python.exe"
$venvPip = ".\venv\Scripts\pip.exe"

# Actualizar pip silenciosamente
Write-Host "Actualizando pip..." -ForegroundColor Gray
& $venvPython -m pip install --upgrade pip --quiet 2>$null

# Instalar dependencias
Write-Host "Instalando dependencias desde requirements.txt..." -ForegroundColor Gray
& $venvPip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Falló la instalación de dependencias de Python" -ForegroundColor Red
    Write-Host "Intentando instalación detallada..." -ForegroundColor Yellow
    & $venvPip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        exit 1
    }
}

Write-Host "Dependencias de Python instaladas correctamente" -ForegroundColor Green
Write-Host ""

# Instalar dependencias del Frontend (Node.js)
Write-Host "[4/4] Instalando dependencias del Frontend (Node.js)..." -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Gray

$frontendPath = Join-Path $projectRoot "Frontend\react-app"
Set-Location $frontendPath

Write-Host "Instalando paquetes de Node.js (esto puede tardar varios minutos)..." -ForegroundColor Yellow

# Redirigir warnings de npm a null para salida más limpia
$env:NPM_CONFIG_LOGLEVEL = "error"
npm install --silent 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalación con warnings, reintentando con salida completa..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Falló la instalación de dependencias de Node.js" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Dependencias de Node.js instaladas correctamente" -ForegroundColor Green
Write-Host ""

# Regresar al directorio raíz
Set-Location $projectRoot

# Resumen final
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ¡Instalación Completada!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Todas las dependencias se han instalado correctamente." -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Configurar la base de datos PostgreSQL" -ForegroundColor White
Write-Host "2. Crear el archivo .env en backend/app/DB/" -ForegroundColor White
Write-Host "3. Ejecutar: .\Scripts\start_DocuSeal.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Para más información, consulta el archivo README.md" -ForegroundColor Gray
Write-Host ""
