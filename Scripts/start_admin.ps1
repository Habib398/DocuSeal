# Script para iniciar DocuSeal Admin API (API Administrativa) + Frontend React
# Puerto Backend: 8002
# Puerto Frontend: 3000

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DocuSeal Admin API + Frontend" -ForegroundColor Cyan
Write-Host "  Backend: 8002 | Frontend: 3000" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar a la raíz del repositorio (para que las importaciones por paquete funcionen)
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

# Iniciar Frontend React en un proceso separado
Write-Host "Iniciando Frontend React..." -ForegroundColor Green
Write-Host "Frontend disponible en: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""

$frontend_job = Start-Job -ScriptBlock {
	param($path)
	Set-Location -Path $path
	npm run dev
} -ArgumentList $frontend_path

# Esperar un momento para que el frontend inicie
Start-Sleep -Seconds 2

# Iniciar el servidor backend con uvicorn
Write-Host "Iniciando API administrativa..." -ForegroundColor Green
Write-Host "Documentación disponible en: http://localhost:8002/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANTE: Accede a la aplicación desde: http://localhost:3000" -ForegroundColor Magenta
Write-Host "Presiona Ctrl+C para detener ambos servicios" -ForegroundColor Red
Write-Host ""

# Preferir el python del entorno virtual .venv para garantizar que se usen
# las dependencias instaladas en el proyecto (uvicorn, psycopg2, bcrypt, etc.).
$venv_python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

try {
	if (Test-Path $venv_python) {
		Write-Host "Usando python del virtualenv: $venv_python" -ForegroundColor Green
		# Usar la ruta de paquete completa para evitar ambigüedad en la importación
		& $venv_python -m uvicorn backend.app.api_admin.main:app --host 0.0.0.0 --port 8002 --reload
	} else {
		Write-Host "Virtualenv no encontrado, se usará el comando 'uvicorn' del sistema" -ForegroundColor Yellow
		uvicorn backend.app.api_admin.main:app --host 0.0.0.0 --port 8002 --reload
	}
} finally {
	# Detener el job del frontend cuando se detenga el backend
	Write-Host "`nDeteniendo Frontend React..." -ForegroundColor Yellow
	Stop-Job -Job $frontend_job
	Remove-Job -Job $frontend_job
	Write-Host "Servicios detenidos." -ForegroundColor Green
}
