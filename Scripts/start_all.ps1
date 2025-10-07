# Script para iniciar ambas APIs de DocuSeal simultáneamente
# Service API: Puerto 8001
# Admin API: Puerto 8002

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DocuSeal - Iniciar Todo" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando ambos servicios..." -ForegroundColor Green
Write-Host "  - Service API: http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host "  - Admin API:   http://localhost:8002/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Presiona Ctrl+C para detener ambos servicios" -ForegroundColor Red
Write-Host ""

# Función para iniciar proceso en background
function Start-ApiService {
    param(
        [string]$Path,
        [int]$Port,
        [string]$Name
    )
    
    $job = Start-Job -ScriptBlock {
        param($p, $port)
        Set-Location $p
        uvicorn main:app --host 0.0.0.0 --port $port --reload
    } -ArgumentList $Path, $Port
    
    return $job
}

# Rutas absolutas
$servicePath = Join-Path $PSScriptRoot "backend\app\api_service"
$adminPath = Join-Path $PSScriptRoot "backend\app\api_admin"

# Iniciar ambos servicios
Write-Host "[1/2] Iniciando Service API..." -ForegroundColor Green
$serviceJob = Start-ApiService -Path $servicePath -Port 8001 -Name "Service"

Start-Sleep -Seconds 2

Write-Host "[2/2] Iniciando Admin API..." -ForegroundColor Green
$adminJob = Start-ApiService -Path $adminPath -Port 8002 -Name "Admin"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "Ambos servicios iniciados correctamente!" -ForegroundColor Green
Write-Host ""

# Mantener el script corriendo y mostrar outputs
try {
    while ($true) {
        # Mostrar output del Service API
        Receive-Job -Job $serviceJob -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "[Service] $_" -ForegroundColor Cyan
        }
        
        # Mostrar output del Admin API
        Receive-Job -Job $adminJob -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "[Admin]   $_" -ForegroundColor Magenta
        }
        
        Start-Sleep -Milliseconds 500
    }
}
finally {
    Write-Host ""
    Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
    Stop-Job -Job $serviceJob, $adminJob
    Remove-Job -Job $serviceJob, $adminJob
    Write-Host "Servicios detenidos." -ForegroundColor Red
}
