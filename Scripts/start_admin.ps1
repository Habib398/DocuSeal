# Script para iniciar DocuSeal Admin API (API Administrativa)
# Puerto: 8002

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DocuSeal Admin API" -ForegroundColor Cyan
Write-Host "  Puerto: 8002" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar a la raíz del repositorio (para que las importaciones por paquete funcionen)
$repo_root = Join-Path $PSScriptRoot ".."
Set-Location -Path $repo_root

Write-Host "Iniciando API administrativa..." -ForegroundColor Green
Write-Host "Documentación disponible en: http://localhost:8002/docs" -ForegroundColor Yellow
Write-Host "URL de acceso disponible en: http://127.0.0.1:8002/login" -ForegroundColor Yellow
Write-Host ""

# Iniciar el servidor con uvicorn
# Preferir el python del entorno virtual .venv para garantizar que se usen
# las dependencias instaladas en el proyecto (uvicorn, psycopg2, bcrypt, etc.).
$venv_python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"
if (Test-Path $venv_python) {
	Write-Host "Usando python del virtualenv: $venv_python" -ForegroundColor Green
	# Usar la ruta de paquete completa para evitar ambigüedad en la importación
	& $venv_python -m uvicorn backend.app.api_admin.main:app --host 0.0.0.0 --port 8002 --reload
} else {
	Write-Host "Virtualenv no encontrado, se usará el comando 'uvicorn' del sistema" -ForegroundColor Yellow
	uvicorn backend.app.api_admin.main:app --host 0.0.0.0 --port 8002 --reload
}
