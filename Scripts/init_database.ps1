# Script de Inicialización de Base de Datos PostgreSQL para DocuSeal
# Este script crea la base de datos y las tablas necesarias

param(
    [string]$EnvPath = "",
    [switch]$Silent = $false
)

# Configuración de colores
$ColorGreen = "Green"
$ColorRed = "Red"
$ColorYellow = "Yellow"
$ColorCyan = "Cyan"

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    if (-not $Silent) {
        $color = switch ($Status) {
            "OK" { $ColorGreen }
            "ERROR" { $ColorRed }
            "WARNING" { $ColorYellow }
            "INFO" { $ColorCyan }
            default { "White" }
        }
        Write-Host "[$Status] $Message" -ForegroundColor $color
    }
}

function Load-EnvFile {
    param([string]$Path)
    
    $env_vars = @{}
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^\s*([^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                # Remover comillas si existen
                $value = $value -replace '^"(.*)"$', '$1'
                $env_vars[$key] = $value
            }
        }
        return $env_vars
    }
    return $null
}

function Find-EnvFile {
    $locations = @(
        (Join-Path $PSScriptRoot "..\\.env"),
        (Join-Path $PSScriptRoot "..\backend\app\DB\.env"),
        (Join-Path $PSScriptRoot ".env"),
        (Join-Path (Get-Location) ".env")
    )
    
    foreach ($location in $locations) {
        if (Test-Path $location) {
            return (Resolve-Path $location).Path
        }
    }
    return $null
}

function Test-PostgreSQLConnection {
    param(
        [string]$HostName,
        [string]$Port,
        [string]$User,
        [string]$Password
    )
    
    try {
        # Intentar conexión básica usando psql si está disponible
        $pgPath = Get-Command psql -ErrorAction SilentlyContinue
        if ($pgPath) {
            $env:PGPASSWORD = $Password
            & psql -h $HostName -p $Port -U $User -d "postgres" -c "SELECT 1" 2>&1 | Out-Null
            $env:PGPASSWORD = ""
            return $?
        }
        
        # Fallback: usar PowerShell para probar conexión
        $ConnectionString = "Server=$HostName;Port=$Port;User Id=$User;Password=$Password;Database=postgres;"
        $Connection = New-Object System.Data.Odbc.OdbcConnection($ConnectionString)
        $Connection.Open()
        $Connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

function Create-Database {
    param(
        [string]$HostName,
        [string]$Port,
        [string]$Database,
        [string]$User,
        [string]$Password
    )
    
    try {
        $env:PGPASSWORD = $Password
        
        # Verificar si la BD ya existe
        $result = & psql -h $HostName -p $Port -U $User -d "postgres" -tAc "SELECT 1 FROM pg_database WHERE datname='$Database'" 2>&1
        
        if ($result -eq "1") {
            Write-Status "Base de datos '$Database' ya existe" "OK"
            return $true
        }
        
        # Crear la BD
        Write-Status "Creando base de datos '$Database'..." "INFO"
        & psql -h $HostName -p $Port -U $User -d "postgres" -c "CREATE DATABASE $Database" 2>&1
        
        $env:PGPASSWORD = ""
        
        if ($?) {
            Write-Status "Base de datos '$Database' creada correctamente" "OK"
            return $true
        }
        else {
            Write-Status "No se pudo crear la base de datos '$Database'" "ERROR"
            return $false
        }
    }
    catch {
        Write-Status "Error creando base de datos: $_" "ERROR"
        return $false
    }
    finally {
        $env:PGPASSWORD = ""
    }
}

function Initialize-Tables {
    param(
        [string]$PythonPath,
        [string]$DbInitScript
    )
    
    try {
        Write-Status "Creando tablas de base de datos..." "INFO"
        
        if (-not (Test-Path $DbInitScript)) {
            Write-Status "Archivo de inicialización no encontrado: $DbInitScript" "ERROR"
            return $false
        }
        
        # Ejecutar el script de inicialización y capturar salida
        $output = & $PythonPath $DbInitScript 2>&1
        $exitCode = $LASTEXITCODE
        
        # Mostrar la salida de Python
        if ($output) {
            Write-Host $output
        }
        
        # Verificar si fue exitoso
        if ($exitCode -eq 0) {
            Write-Status "Tablas creadas correctamente" "OK"
            return $true
        }
        else {
            Write-Status "Error creando tablas (Código: $exitCode)" "ERROR"
            return $false
        }
    }
    catch {
        Write-Status "Error durante inicialización de tablas: $_" "ERROR"
        return $false
    }
}

# ==================== MAIN ====================

Write-Status "========================================" "INFO"
Write-Status "  Inicializador de BD - DocuSeal" "INFO"
Write-Status "========================================" "INFO"
Write-Status "" "INFO"

# Buscar archivo .env
if (-not $EnvPath) {
    $EnvPath = Find-EnvFile
}

if (-not $EnvPath -or -not (Test-Path $EnvPath)) {
    Write-Status "ERROR: No se encontró archivo .env" "ERROR"
    Write-Status "Ubicaciones buscadas:" "INFO"
    Write-Status "  - Raíz del proyecto" "INFO"
    Write-Status "  - backend/app/DB/" "INFO"
    exit 1
}

Write-Status "Archivo .env encontrado: $EnvPath" "OK"
Write-Status "" "INFO"

# Cargar variables de entorno
$env_vars = Load-EnvFile $EnvPath

if (-not $env_vars) {
    Write-Status "ERROR: No se pudo cargar el archivo .env" "ERROR"
    exit 1
}

# Obtener configuración de BD
$db_host = if ($env_vars["DB_HOST"]) { $env_vars["DB_HOST"] } else { "localhost" }
$db_port = if ($env_vars["DB_PORT"]) { $env_vars["DB_PORT"] } else { "5432" }
$db_name = if ($env_vars["DB_NAME"]) { $env_vars["DB_NAME"] } else { "certificados_pac" }
$db_user = $env_vars["DB_USER"]
$db_password = $env_vars["DB_PASSWORD"]

if (-not $db_user -or -not $db_password) {
    Write-Status "ERROR: Credenciales de BD incompletas en .env" "ERROR"
    Write-Status "Se requieren: DB_USER y DB_PASSWORD" "ERROR"
    exit 1
}

Write-Status "Configuración de BD:" "INFO"
Write-Status "  Host: $db_host" "INFO"
Write-Status "  Puerto: $db_port" "INFO"
Write-Status "  BD: $db_name" "INFO"
Write-Status "  Usuario: $db_user" "INFO"
Write-Status "" "INFO"

# Verificar conexión a PostgreSQL
Write-Status "Verificando conexión a PostgreSQL..." "INFO"
$pgPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $pgPath) {
    Write-Status "WARNING: PostgreSQL CLI (psql) no encontrado en PATH" "WARNING"
    Write-Status "Intentando con rutas predeterminadas..." "INFO"
    
    $psql_paths = @(
        "C:\Program Files\PostgreSQL\18\bin\psql.exe",
        "C:\Program Files\PostgreSQL\17\bin\psql.exe",
        "C:\Program Files\PostgreSQL\16\bin\psql.exe",
        "C:\Program Files\PostgreSQL\15\bin\psql.exe"
    )
    
    $psql_found = $false
    foreach ($path in $psql_paths) {
        if (Test-Path $path) {
            $psql_found = $true
            $env:PATH = (Split-Path $path) + ";$env:PATH"
            Write-Status "PostgreSQL encontrado en: $path" "OK"
            break
        }
    }
    
    if (-not $psql_found) {
        Write-Status "ERROR: No se pudo encontrar PostgreSQL" "ERROR"
        Write-Status "Por favor, instala PostgreSQL o agrega su ruta a PATH" "ERROR"
        exit 1
    }
}

# Probar conexión
if (-not (Test-PostgreSQLConnection -HostName $db_host -Port $db_port -User $db_user -Password $db_password)) {
    Write-Status "ERROR: No se puede conectar a PostgreSQL" "ERROR"
    Write-Status "Verifica:" "INFO"
    Write-Status "  - PostgreSQL está ejecutándose" "INFO"
    Write-Status "  - Host: $db_host" "INFO"
    Write-Status "  - Puerto: $db_port" "INFO"
    Write-Status "  - Credenciales correctas" "INFO"
    exit 1
}

Write-Status "Conexión a PostgreSQL exitosa" "OK"
Write-Status "" "INFO"

# Crear BD
if (-not (Create-Database -HostName $db_host -Port $db_port -Database $db_name -User $db_user -Password $db_password)) {
    Write-Status "ERROR: No se pudo crear/verificar la base de datos" "ERROR"
    exit 1
}

Write-Status "" "INFO"

# Inicializar tablas
$db_init_script = Join-Path $PSScriptRoot "..\backend\app\DB\settings.py"

# Encontrar Python en el venv
$python_paths = @(
    (Join-Path $PSScriptRoot "..\venv\Scripts\python.exe"),
    (Join-Path $PSScriptRoot "..\..\..\venv\Scripts\python.exe"),
    "python"
)

$python_found = $false
$python_exe = $null

foreach ($path in $python_paths) {
    if (Test-Path $path) {
        $python_found = $true
        $python_exe = (Resolve-Path $path).Path
        Write-Status "Python encontrado: $python_exe" "OK"
        break
    }
    elseif ($path -eq "python") {
        $check = Get-Command python -ErrorAction SilentlyContinue
        if ($check) {
            $python_found = $true
            $python_exe = $check.Source
            Write-Status "Python encontrado en PATH: $python_exe" "OK"
            break
        }
    }
}

if (-not $python_found) {
    Write-Status "ERROR: No se pudo encontrar Python" "ERROR"
    exit 1
}

Write-Status "" "INFO"

if (-not (Initialize-Tables -PythonPath $python_exe -DbInitScript $db_init_script)) {
    Write-Status "ERROR: No se pudieron crear las tablas" "ERROR"
    exit 1
}

Write-Status "" "INFO"
Write-Status "========================================" "INFO"
Write-Status "  Inicialización Completada" "INFO"
Write-Status "========================================" "INFO"
Write-Status "" "INFO"
Write-Status "La base de datos está lista para usar" "OK"
Write-Status "" "INFO"

exit 0
