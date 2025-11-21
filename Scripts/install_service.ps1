# Script de instalación automática del servicio DocuSeal con NSSM

# IMPORTANTE: Ejecutar como Administrador

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Instalador DocuSeal Service" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si se ejecuta como administrador
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
	Write-Host "ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
	Write-Host "Por favor, ejecuta PowerShell como Administrador y vuelve a intentar." -ForegroundColor Yellow
	Read-Host "Presiona Enter para cerrar"
	exit 1
}

# Configuración
$service_name = "DocuSealService"
$exe_path = "C:\Users\Abitt\Desktop\DespliegueV2\DocuSeal-main\dist\DocuSealService.exe"
$work_dir = "C:\Users\Abitt\Desktop\DespliegueV2\DocuSeal-main"
$log_dir = "$env:LOCALAPPDATA\DocuSeal\logs"

# Descargar NSSM si no existe
Write-Host "Verificando NSSM..." -ForegroundColor Yellow
$nssm_path = "$env:TEMP\nssm-2.24-101-g897c7ad\win64\nssm.exe"
$nssm_zip = "$env:TEMP\nssm.zip"

if (-not (Test-Path $nssm_path)) {
	Write-Host "Descargando NSSM..." -ForegroundColor Green
	try {
		$url = "https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip"
		Invoke-WebRequest -Uri $url -OutFile $nssm_zip -ErrorAction Stop
		Write-Host "Extrayendo NSSM..." -ForegroundColor Green
		Expand-Archive -Path $nssm_zip -DestinationPath "$env:TEMP\" -Force
		Write-Host "NSSM descargado e instalado" -ForegroundColor Green
	} catch {
		Write-Host "ERROR: No se pudo descargar NSSM" -ForegroundColor Red
		Write-Host "Por favor, descárgalo manualmente desde: https://nssm.cc/download" -ForegroundColor Yellow
		Read-Host "Presiona Enter para cerrar"
		exit 1
	}
} else {
	Write-Host "NSSM ya existe" -ForegroundColor Green
}

# Verificar que el ejecutable existe
if (-not (Test-Path $exe_path)) {
	Write-Host "ERROR: $exe_path no encontrado" -ForegroundColor Red
	Read-Host "Presiona Enter para cerrar"
	exit 1
}

Write-Host ""
Write-Host "Configurando el servicio..." -ForegroundColor Yellow

# Eliminar servicio anterior si existe
$service_exists = Get-Service -Name $service_name -ErrorAction SilentlyContinue
if ($service_exists) {
	Write-Host "Deteniendo servicio existente..." -ForegroundColor Yellow
	Stop-Service -Name $service_name -Force -ErrorAction SilentlyContinue
	Write-Host "Eliminando servicio existente..." -ForegroundColor Yellow
	& $nssm_path remove $service_name confirm 2>&1 | Out-Null
	Start-Sleep -Seconds 2
}

# Crear directorio de logs
New-Item -ItemType Directory -Path $log_dir -Force | Out-Null

# Instalar el servicio
Write-Host "Instalando servicio: $service_name" -ForegroundColor Green
& $nssm_path install $service_name "$exe_path" | Out-Null

# Configurar
Write-Host "Configurando parámetros del servicio..." -ForegroundColor Green
& $nssm_path set $service_name AppDirectory "$work_dir" | Out-Null
& $nssm_path set $service_name AppExit Default Restart | Out-Null
& $nssm_path set $service_name AppRestartDelay 5000 | Out-Null
& $nssm_path set $service_name AppStdout "$log_dir\stdout.log" | Out-Null
& $nssm_path set $service_name AppStderr "$log_dir\stderr.log" | Out-Null

# Iniciar el servicio
Write-Host "Iniciando servicio..." -ForegroundColor Green
& $nssm_path start $service_name

# Esperar a que inicie
Start-Sleep -Seconds 3

# Verificar estado
$service_status = (& $nssm_path status $service_name)

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Instalación Completada" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Estado del servicio: $service_status" -ForegroundColor Green
Write-Host ""
Write-Host "URLs de acceso:" -ForegroundColor Cyan
Write-Host "  - API Admin: http://localhost:8000/admin" -ForegroundColor White
Write-Host "  - API Service: http://localhost:8000/service" -ForegroundColor White
Write-Host "  - Docs: http://localhost:8000/service/docs" -ForegroundColor White
Write-Host ""
Write-Host "Directorio de logs: $log_dir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Comandos útiles:" -ForegroundColor Cyan
Write-Host "  Detener:   nssm stop $service_name" -ForegroundColor White
Write-Host "  Iniciar:   nssm start $service_name" -ForegroundColor White
Write-Host "  Reiniciar: nssm restart $service_name" -ForegroundColor White
Write-Host "  Eliminar:  nssm remove $service_name confirm" -ForegroundColor White
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Read-Host "Presiona Enter para cerrar"
