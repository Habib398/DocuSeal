# Script para iniciar DocuSeal Service API (API Pública)
# Puerto: 8001

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DocuSeal Service API" -ForegroundColor Cyan
Write-Host "  Puerto: 8001" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar al directorio del servicio
Set-Location -Path "$PSScriptRoot\backend\app\api_service"

Write-Host "Iniciando API de servicios públicos..." -ForegroundColor Green
Write-Host "Documentación disponible en: http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host ""

# Iniciar el servidor con uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
