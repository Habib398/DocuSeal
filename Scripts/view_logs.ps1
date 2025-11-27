# Script para ver los logs del servicio DocuSeal de forma rápida

$log_dir = "$env:APPDATA\DocuSeal\logs"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Viewer de Logs DocuSeal Service" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $log_dir)) {
	Write-Host "ERROR: Directorio de logs no encontrado" -ForegroundColor Red
	Write-Host "Ubicación esperada: $log_dir" -ForegroundColor Yellow
	Write-Host ""
	Write-Host "Verifica que el servicio está instalado y ha sido ejecutado." -ForegroundColor Yellow
	Read-Host "Presiona Enter para cerrar"
	exit 1
}

# Listar archivos disponibles
$log_files = @(Get-ChildItem $log_dir -ErrorAction SilentlyContinue)

if ($log_files.Count -eq 0) {
	Write-Host "Sin archivos de log" -ForegroundColor Yellow
	Read-Host "Presiona Enter para cerrar"
	exit 0
}

Write-Host "Archivos de log disponibles:" -ForegroundColor Green
Write-Host ""

# Mostrar opciones
$i = 1
foreach ($file in $log_files) {
	$size = "{0:N0} bytes" -f $file.Length
	$date = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
	Write-Host "$i) $($file.Name) [$size] (Modificado: $date)" -ForegroundColor Cyan
	$i++
}

Write-Host ""
Write-Host "Opciones:" -ForegroundColor Green
Write-Host "  T) Ver stderr (errores) - Últimas 50 líneas" -ForegroundColor White
Write-Host "  S) Ver stdout (salida estándar) - Últimas 50 líneas" -ForegroundColor White
Write-Host "  TE) Ver stderr COMPLETO" -ForegroundColor White
Write-Host "  SE) Ver stdout COMPLETO" -ForegroundColor White
Write-Host "  E) Explorador (abrir carpeta)" -ForegroundColor White
Write-Host "  Q) Salir" -ForegroundColor White
Write-Host ""

do {
	$choice = Read-Host "Selecciona una opción (T/S/TE/SE/E/Q)"
	
	switch ($choice.ToUpper()) {
		"T" {
			$stderr = Join-Path $log_dir "stderr.log"
			if (Test-Path $stderr) {
				Write-Host ""
				Write-Host "==== ÚLTIMAS 50 LÍNEAS DE STDERR ====" -ForegroundColor Yellow
				Write-Host ""
				Get-Content $stderr -Tail 50 -ErrorAction SilentlyContinue
			} else {
				Write-Host "Archivo stderr.log no encontrado" -ForegroundColor Red
			}
			Write-Host ""
			Read-Host "Presiona Enter para continuar"
		}
		"S" {
			$stdout = Join-Path $log_dir "stdout.log"
			if (Test-Path $stdout) {
				Write-Host ""
				Write-Host "==== ÚLTIMAS 50 LÍNEAS DE STDOUT ====" -ForegroundColor Yellow
				Write-Host ""
				Get-Content $stdout -Tail 50 -ErrorAction SilentlyContinue
			} else {
				Write-Host "Archivo stdout.log no encontrado" -ForegroundColor Red
			}
			Write-Host ""
			Read-Host "Presiona Enter para continuar"
		}
		"TE" {
			$stderr = Join-Path $log_dir "stderr.log"
			if (Test-Path $stderr) {
				Write-Host ""
				Write-Host "==== ARCHIVO STDERR COMPLETO ====" -ForegroundColor Yellow
				Write-Host ""
				Get-Content $stderr -ErrorAction SilentlyContinue
			} else {
				Write-Host "Archivo stderr.log no encontrado" -ForegroundColor Red
			}
			Write-Host ""
			Read-Host "Presiona Enter para continuar"
		}
		"SE" {
			$stdout = Join-Path $log_dir "stdout.log"
			if (Test-Path $stdout) {
				Write-Host ""
				Write-Host "==== ARCHIVO STDOUT COMPLETO ====" -ForegroundColor Yellow
				Write-Host ""
				Get-Content $stdout -ErrorAction SilentlyContinue
			} else {
				Write-Host "Archivo stdout.log no encontrado" -ForegroundColor Red
			}
			Write-Host ""
			Read-Host "Presiona Enter para continuar"
		}
		"E" {
			explorer.exe $log_dir
			Write-Host "Abriendo carpeta de logs..." -ForegroundColor Green
			Start-Sleep -Seconds 2
			exit 0
		}
		"Q" {
			exit 0
		}
		default {
			Write-Host "Opción no válida" -ForegroundColor Red
		}
	}
	
	Clear-Host
	Write-Host "=====================================" -ForegroundColor Cyan
	Write-Host "  Viewer de Logs DocuSeal Service" -ForegroundColor Cyan
	Write-Host "=====================================" -ForegroundColor Cyan
	Write-Host ""
	
} while ($choice.ToUpper() -ne "Q")

Write-Host "Saliendo..." -ForegroundColor Green
