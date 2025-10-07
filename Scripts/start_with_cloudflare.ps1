# Script para iniciar DocuSeal con Cloudflare Tunnel
# Expone tus APIs locales con una URL pública temporal GRATIS

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  DocuSeal - Cloudflare Tunnel" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si cloudflared está instalado
$cloudflaredPath = Get-Command cloudflared -ErrorAction SilentlyContinue

if (-not $cloudflaredPath) {
    Write-Host "[INFO] Cloudflared no encontrado. Instalando..." -ForegroundColor Yellow
    Write-Host ""
    
    # Descargar cloudflared para Windows
    $downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    $installPath = "$HOME\cloudflared"
    $exePath = "$installPath\cloudflared.exe"
    
    # Crear directorio
    New-Item -ItemType Directory -Path $installPath -Force | Out-Null
    
    Write-Host "[INFO] Descargando cloudflared..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath
        Write-Host "[OK] Cloudflared descargado correctamente" -ForegroundColor Green
        $cloudflaredPath = $exePath
    } catch {
        Write-Host "[ERROR] No se pudo descargar cloudflared: $_" -ForegroundColor Red
        Write-Host "[INFO] Instalalo manualmente: winget install cloudflare.cloudflared" -ForegroundColor Yellow
        exit 1
    }
} else {
    $cloudflaredPath = $cloudflaredPath.Source
    Write-Host "[OK] Cloudflared encontrado en: $cloudflaredPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Iniciando Servicios" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "[INFO] Activando entorno virtual..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "[WARNING] No se encontró entorno virtual en .venv" -ForegroundColor Yellow
}

# Iniciar API Service (Puerto 8001)
Write-Host "[INFO] Iniciando API Service en puerto 8001..." -ForegroundColor Yellow
$currentDir = Get-Location
$serviceCommand = "cd '$currentDir'; .\.venv\Scripts\Activate.ps1; Write-Host 'Iniciando API Service...' -ForegroundColor Green; uvicorn backend.app.api_service.main:app --host 0.0.0.0 --port 8001 --reload"
$serviceProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $serviceCommand -PassThru -WindowStyle Normal

Start-Sleep -Seconds 5

# Iniciar API Admin (Puerto 8002)
Write-Host "[INFO] Iniciando API Admin en puerto 8002..." -ForegroundColor Yellow
$adminCommand = "cd '$currentDir'; .\.venv\Scripts\Activate.ps1; Write-Host 'Iniciando API Admin...' -ForegroundColor Green; uvicorn backend.app.api_admin.main:app --host 0.0.0.0 --port 8002 --reload"
$adminProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminCommand -PassThru -WindowStyle Normal

Start-Sleep -Seconds 5

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Cloudflare Tunnels" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar túnel para API Service
Write-Host "[INFO] Creando túnel Cloudflare para API Service (puerto 8001)..." -ForegroundColor Yellow
$tunnelService = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$cloudflaredPath' tunnel --url http://localhost:8001" -PassThru -WindowStyle Normal

Start-Sleep -Seconds 3

# Iniciar túnel para API Admin
Write-Host "[INFO] Creando túnel Cloudflare para API Admin (puerto 8002)..." -ForegroundColor Yellow
$tunnelAdmin = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$cloudflaredPath' tunnel --url http://localhost:8002" -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  ¡Servicios Iniciados!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "📌 URLs Locales:" -ForegroundColor Cyan
Write-Host "   - API Service: http://localhost:8001" -ForegroundColor White
Write-Host "   - API Admin:   http://localhost:8002" -ForegroundColor White
Write-Host ""
Write-Host "🌐 URLs Públicas Cloudflare:" -ForegroundColor Cyan
Write-Host "   - Revisa las ventanas de PowerShell que se abrieron" -ForegroundColor Yellow
Write-Host "   - Busca líneas como: 'https://xxxx.trycloudflare.com'" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 Documentación:" -ForegroundColor Cyan
Write-Host "   - API Service Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host "   - API Admin Docs:   http://localhost:8002/docs" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Presiona Ctrl+C para detener todos los servicios" -ForegroundColor Yellow
Write-Host ""

# Esperar a que el usuario presione Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "[INFO] Deteniendo servicios..." -ForegroundColor Yellow
    
    # Detener procesos
    Stop-Process -Id $serviceProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $adminProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $tunnelService.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $tunnelAdmin.Id -Force -ErrorAction SilentlyContinue
    
    Write-Host "[OK] Servicios detenidos" -ForegroundColor Green
}
