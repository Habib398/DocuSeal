# Script para verificar el estado de DocuSeal Service

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Verificador DocuSeal Service" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$service_name = "DocuSealService"
$port = 8000
# Usar Roaming en lugar de Local para consistencia con NSSM
$log_dir = "$env:APPDATA\DocuSeal\logs"

# 1. Verificar si el servicio existe
Write-Host "1. Verificando servicio..." -ForegroundColor Yellow
$service = Get-Service -Name $service_name -ErrorAction SilentlyContinue

if ($service) {
	$status = $service.Status
	$start_type = $service.StartType
	
	Write-Host "   ✓ Servicio encontrado" -ForegroundColor Green
	Write-Host "   - Estado: $status" -ForegroundColor White
	Write-Host "   - Tipo de inicio: $start_type" -ForegroundColor White
	
	if ($status -eq "Running") {
		Write-Host "   ✓ El servicio está corriendo" -ForegroundColor Green
	} else {
		Write-Host "   ✗ El servicio NO está corriendo" -ForegroundColor Red
	}
} else {
	Write-Host "   ✗ Servicio no encontrado" -ForegroundColor Red
	Write-Host "   → Ejecuta: .\install_service.ps1" -ForegroundColor Yellow
}

Write-Host ""

# 2. Verificar puerto
Write-Host "2. Verificando puerto $port..." -ForegroundColor Yellow
$port_check = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -ErrorAction SilentlyContinue

if ($port_check) {
	Write-Host "   ✓ Puerto $port está abierto" -ForegroundColor Green
} else {
	Write-Host "   ✗ Puerto $port no responde" -ForegroundColor Red
	Write-Host "   → El servicio puede no estar corriendo" -ForegroundColor Yellow
}

Write-Host ""

# 3. Verificar logs
Write-Host "3. Verificando logs..." -ForegroundColor Yellow
if (Test-Path $log_dir) {
	$log_files = Get-ChildItem $log_dir -ErrorAction SilentlyContinue
	if ($log_files) {
		Write-Host "   ✓ Directorio de logs encontrado" -ForegroundColor Green
		Write-Host "   - Ubicación: $log_dir" -ForegroundColor White
		Write-Host "   - Archivos: $($log_files.Count)" -ForegroundColor White
		
		# Mostrar últimas líneas de stderr si existe
		$stderr = Join-Path $log_dir "stderr.log"
		if (Test-Path $stderr) {
			$last_errors = @(Get-Content $stderr -Tail 5 -ErrorAction SilentlyContinue)
			if ($last_errors.Count -gt 0) {
				Write-Host ""
				Write-Host "   Últimas líneas de stderr:" -ForegroundColor Cyan
				foreach ($line in $last_errors) {
					Write-Host "     $line" -ForegroundColor Gray
				}
			}
		}
	} else {
		Write-Host "   ⚠ Directorio de logs existe pero está vacío" -ForegroundColor Yellow
	}
} else {
	Write-Host "   ⚠ Directorio de logs no encontrado" -ForegroundColor Yellow
	Write-Host "   - Ubicación esperada: $log_dir" -ForegroundColor Gray
}

Write-Host ""

# 4. Intentar acceder a la API
Write-Host "4. Verificando API..." -ForegroundColor Yellow
try {
	$response = Invoke-WebRequest -Uri "http://localhost:$port/service/docs" -Method Get -TimeoutSec 2 -ErrorAction Stop
	if ($response.StatusCode -eq 200) {
		Write-Host "   ✓ API está respondiendo correctamente" -ForegroundColor Green
		Write-Host "   → Accede a: http://localhost:$port/service/docs" -ForegroundColor White
	}
} catch {
	Write-Host "   ✗ API no responde" -ForegroundColor Red
	Write-Host "   → Verifica que el servicio está corriendo" -ForegroundColor Yellow
}

Write-Host ""

# 5. Resumen
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Información de Utilidad:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs de acceso:" -ForegroundColor White
Write-Host "  - Admin API: http://localhost:8000/admin" -ForegroundColor Gray
Write-Host "  - Service API: http://localhost:8000/service" -ForegroundColor Gray
Write-Host "  - Documentación: http://localhost:8000/service/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Comandos útiles:" -ForegroundColor White
Write-Host "  - Iniciar: Start-Service -Name DocuSealService" -ForegroundColor Gray
Write-Host "  - Detener: Stop-Service -Name DocuSealService" -ForegroundColor Gray
Write-Host "  - Reiniciar: Restart-Service -Name DocuSealService" -ForegroundColor Gray
Write-Host "  - Ver logs: Get-Content `"$log_dir\stderr.log`" -Tail 50" -ForegroundColor Gray
Write-Host ""
Write-Host "Archivos de configuración:" -ForegroundColor White
Write-Host "  - Guía: INSTALACION_SERVICIO_WINDOWS.md" -ForegroundColor Gray
Write-Host "  - Resumen: RESUMEN_INSTALACION.md" -ForegroundColor Gray
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Read-Host "Presiona Enter para cerrar"
