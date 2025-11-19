# Script para iniciar DocuSeal API

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DocuSeal API" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar a la raíz del repositorio
$repo_root = Join-Path $PSScriptRoot ".."
Set-Location -Path $repo_root

# Verificar si existe la carpeta node_modules en el frontend
$frontend_path = Join-Path $repo_root "Frontend\react-app"
$node_modules = Join-Path $frontend_path "node_modules"

if (-not (Test-Path $node_modules)) {
	Write-Host "Instalando dependencias de Node.js..." -ForegroundColor Yellow
	Set-Location -Path $frontend_path
	npm install
	Set-Location -Path $repo_root
	Write-Host ""
}

# Modo Producción: Compilar el frontend automáticamente
Write-Host "Compilando Frontend React para producción..." -ForegroundColor Green
Set-Location -Path $frontend_path
npm run build
Set-Location -Path $repo_root
Write-Host "Frontend compilado exitosamente" -ForegroundColor Green
Write-Host ""

# Iniciar el servidor backend unificado con uvicorn
Write-Host "Iniciando DocuSeal API..." -ForegroundColor Green
Write-Host "---------------------------------------------------------------"
Write-Host "APIs disponibles:" -ForegroundColor Cyan
Write-Host "  - Admin API: Accede a la interfaz de administración en: http://localhost:8000/admin" -ForegroundColor White
Write-Host "  - Service API: Accede al servicio en: http://localhost:8000/service" -ForegroundColor White
Write-Host "---------------------------------------------------------------"
Write-Host ""
Write-Host "Documentación:" -ForegroundColor Cyan
Write-Host "  - Service: Accede a la documentación del servicio en: http://localhost:8000/service/docs" -ForegroundColor White
Write-Host "---------------------------------------------------------------"
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Red
Write-Host "---------------------------------------------------------------"

# Preferir el python del entorno virtual venv
$venv_python = Join-Path $PSScriptRoot "..\venv\Scripts\python.exe"

try {
	if (Test-Path $venv_python) {
		Write-Host "Usando python del virtualenv: $venv_python" -ForegroundColor Green
		& $venv_python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload --log-level error
	} else {
		Write-Host "Virtualenv no encontrado, se usará el comando 'uvicorn' del sistema" -ForegroundColor Yellow
		uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload --log-level error
	}
} finally {
	Write-Host "`nServidor detenido." -ForegroundColor Green
}
