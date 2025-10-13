# Script para iniciar DocuSeal Service API (API Pública)
# Puerto: 8001

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DocuSeal Service API" -ForegroundColor Cyan
Write-Host "  Puerto: 8001" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Guardar la ubicación original (carpeta DocuSeal)
$originalLocation = "$PSScriptRoot\.."

# Navegar al directorio del servicio (subir un nivel desde Scripts hacia la raíz del proyecto)
# Antes: $PSScriptRoot\backend\app\api_service -> esto buscaba Scripts\backend\..., ruta incorrecta
Set-Location -Path "$PSScriptRoot\..\backend\app\api_service"

Write-Host "Iniciando API de servicios públicos..." -ForegroundColor Green
Write-Host "Documentación disponible en: http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host ""

try {
    # Iniciar el servidor con uvicorn
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}
finally {
    # Siempre volver a la carpeta DocuSeal al finalizar (incluso con Ctrl+C)
    Set-Location -Path $originalLocation
    Write-Host ""
}
