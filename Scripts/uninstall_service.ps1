# Script para uninstalar DocuSeal Service

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Desinstalador DocuSeal Service" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si se ejecuta como administrador
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
	Write-Host "ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
	Read-Host "Presiona Enter para cerrar"
	exit 1
}

$service_name = "DocuSealService"

# Verificar si el servicio existe
$service = Get-Service -Name $service_name -ErrorAction SilentlyContinue

if (-not $service) {
	Write-Host "El servicio '$service_name' no está instalado." -ForegroundColor Yellow
	Read-Host "Presiona Enter para cerrar"
	exit 0
}

# Preguntar confirmación
Write-Host "¿Deseas desinstalar el servicio '$service_name'? (S/N)" -ForegroundColor Yellow
$confirm = Read-Host

if ($confirm -ne "S" -and $confirm -ne "s") {
	Write-Host "Operación cancelada." -ForegroundColor Yellow
	Read-Host "Presiona Enter para cerrar"
	exit 0
}

# Detener el servicio
Write-Host "Deteniendo el servicio..." -ForegroundColor Green
Stop-Service -Name $service_name -Force -ErrorAction SilentlyContinue

# Esperar a que se detenga
Start-Sleep -Seconds 2

# Desinstalar usando SC
Write-Host "Desinstalando el servicio..." -ForegroundColor Green
$output = & sc.exe delete $service_name

# Verificar
if ($LASTEXITCODE -eq 0) {
	Write-Host ""
	Write-Host "=====================================" -ForegroundColor Cyan
	Write-Host "  Desinstalación Completada" -ForegroundColor Green
	Write-Host "=====================================" -ForegroundColor Cyan
	Write-Host ""
	Write-Host "El servicio '$service_name' ha sido desinstalado correctamente." -ForegroundColor Green
} else {
	Write-Host ""
	Write-Host "=====================================" -ForegroundColor Cyan
	Write-Host "  Error en la Desinstalación" -ForegroundColor Red
	Write-Host "=====================================" -ForegroundColor Cyan
	Write-Host ""
	Write-Host "Hubo un error al desinstalar el servicio." -ForegroundColor Red
	Write-Host "Intenta ejecutar el comando manualmente: sc.exe delete $service_name" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Presiona Enter para cerrar"
