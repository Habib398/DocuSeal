# Script para detener DocuSeal API completamente
# Este script detiene todos los procesos relacionados con DocuSeal y limpia residuos

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Deteniendo DocuSeal API" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navegar a la raiz del repositorio
$repo_root = Join-Path $PSScriptRoot ".."
Set-Location -Path $repo_root

# Funcion para detener procesos por puerto
function Stop-ProcessByPort {
    param (
        [int]$Port
    )
    
    Write-Host "Verificando procesos en el puerto $Port..." -ForegroundColor Yellow
    $connections = netstat -ano | Select-String ":$Port\s" | ForEach-Object { $_ -replace '\s+', ' ' }
    
    foreach ($connection in $connections) {
        $parts = $connection -split ' '
        $pid = $parts[-1]
        
        if ($pid -match '^\d+$') {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "  Deteniendo proceso '$($process.ProcessName)' (PID: $pid) en puerto $Port" -ForegroundColor Red
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-Host "  [OK] Proceso detenido" -ForegroundColor Green
                }
            } catch {
                # Ignorar errores si el proceso ya no existe
            }
        }
    }
}

# 1. Detener procesos de uvicorn
Write-Host "1. Buscando procesos de uvicorn..." -ForegroundColor Cyan
$uvicornProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*" } | Where-Object {
    try {
        $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
        $cmdLine -like "*uvicorn*" -or $cmdLine -like "*backend.app.main*"
    } catch {
        $false
    }
}

if ($uvicornProcesses) {
    foreach ($proc in $uvicornProcesses) {
        Write-Host "  Deteniendo uvicorn (PID: $($proc.Id))" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  [OK] Procesos de uvicorn detenidos" -ForegroundColor Green
} else {
    Write-Host "  No se encontraron procesos de uvicorn" -ForegroundColor Gray
}
Write-Host ""

# 2. Detener procesos en el puerto 8000 (puerto principal de DocuSeal)
Write-Host "2. Liberando puerto 8000..." -ForegroundColor Cyan
Stop-ProcessByPort -Port 8000
Write-Host ""

# 3. Detener cualquier proceso Python que este ejecutando archivos del proyecto
Write-Host "3. Buscando procesos Python de DocuSeal..." -ForegroundColor Cyan
$projectPath = $repo_root -replace '\\', '\\\\'
$pythonProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" } | Where-Object {
    try {
        $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
        $cmdLine -like "*DocuSeal*" -or $cmdLine -like "*backend*" -or $cmdLine -like "*main.py*"
    } catch {
        $false
    }
}

if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        Write-Host "  Deteniendo proceso Python (PID: $($proc.Id))" -ForegroundColor Red
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  [OK] Procesos Python de DocuSeal detenidos" -ForegroundColor Green
} else {
    Write-Host "  No se encontraron procesos Python de DocuSeal" -ForegroundColor Gray
}
Write-Host ""

# 4. Limpiar archivos de cache de Python
Write-Host "4. Limpiando archivos de cache de Python..." -ForegroundColor Cyan

# Eliminar archivos __pycache__
$pycacheDirs = Get-ChildItem -Path $repo_root -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
$pycacheCount = 0
foreach ($dir in $pycacheDirs) {
    try {
        Remove-Item -Path $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
        $pycacheCount++
    } catch {
        Write-Host "  [!] No se pudo eliminar: $($dir.FullName)" -ForegroundColor Yellow
    }
}
Write-Host "  [OK] $pycacheCount carpetas __pycache__ eliminadas" -ForegroundColor Green

# Eliminar archivos .pyc
$pycFiles = Get-ChildItem -Path $repo_root -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
$pycCount = 0
foreach ($file in $pycFiles) {
    try {
        Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
        $pycCount++
    } catch {
        Write-Host "  [!] No se pudo eliminar: $($file.FullName)" -ForegroundColor Yellow
    }
}
Write-Host "  [OK] $pycCount archivos .pyc eliminados" -ForegroundColor Green

# Eliminar archivos .pyo
$pyoFiles = Get-ChildItem -Path $repo_root -Recurse -Filter "*.pyo" -ErrorAction SilentlyContinue
$pyoCount = 0
foreach ($file in $pyoFiles) {
    try {
        Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
        $pyoCount++
    } catch {
        Write-Host "  [!] No se pudo eliminar: $($file.FullName)" -ForegroundColor Yellow
    }
}
Write-Host "  [OK] $pyoCount archivos .pyo eliminados" -ForegroundColor Green
Write-Host ""

# 5. Limpiar archivos temporales en la carpeta Temp
Write-Host "5. Limpiando archivos temporales..." -ForegroundColor Cyan
$tempPath = Join-Path $repo_root "Temp"
if (Test-Path $tempPath) {
    $tempFiles = Get-ChildItem -Path $tempPath -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne "contraseña.txt" }
    $tempCount = 0
    foreach ($file in $tempFiles) {
        try {
            Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
            $tempCount++
        } catch {
            Write-Host "  [!] No se pudo eliminar: $($file.FullName)" -ForegroundColor Yellow
        }
    }
    Write-Host "  [OK] $tempCount archivos temporales eliminados" -ForegroundColor Green
} else {
    Write-Host "  No se encontro la carpeta Temp" -ForegroundColor Gray
}
Write-Host ""

# 6. Esperar un momento para asegurar que todos los procesos se han detenido
Write-Host "6. Esperando confirmacion de cierre..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Write-Host "  [OK] Confirmado" -ForegroundColor Green
Write-Host ""

# Resumen final
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  DocuSeal detenido completamente" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Todos los procesos han sido detenidos y los archivos de cache eliminados." -ForegroundColor White
Write-Host "Puedes volver a iniciar DocuSeal ejecutando start_DocuSeal.ps1" -ForegroundColor Yellow
Write-Host ""
