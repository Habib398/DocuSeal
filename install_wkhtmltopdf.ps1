# Instalación de wkhtmltopdf para Windows Server
# Ejecutar como Administrador

Write-Host "Instalando wkhtmltopdf para generación de PDFs..." -ForegroundColor Green

# URL de descarga (versión estable)
$url = "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe"
$installerPath = "$env:TEMP\wkhtmltopdf-installer.exe"

Write-Host "Descargando wkhtmltopdf..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $url -OutFile $installerPath

Write-Host "Ejecutando instalador..." -ForegroundColor Yellow
Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait

# Agregar al PATH (común en Windows Server)
$wkhtmltopdfPath = "${env:ProgramFiles}\wkhtmltopdf\bin"
if (Test-Path $wkhtmltopdfPath) {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$wkhtmltopdfPath*") {
        $newPath = "$currentPath;$wkhtmltopdfPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "wkhtmltopdf agregado al PATH del sistema" -ForegroundColor Green
    }
}

Write-Host "Verificando instalación..." -ForegroundColor Yellow
try {
    $version = & wkhtmltopdf --version 2>&1
    Write-Host "✓ wkhtmltopdf instalado correctamente" -ForegroundColor Green
    Write-Host "Versión: $version" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Error: wkhtmltopdf no se instaló correctamente" -ForegroundColor Red
    Write-Host "Verifica que el instalador se ejecutó como Administrador" -ForegroundColor Yellow
}

# Limpiar
Remove-Item $installerPath -ErrorAction SilentlyContinue

Write-Host "`nInstalación completada. Reinicia PowerShell para que tome el PATH." -ForegroundColor Green