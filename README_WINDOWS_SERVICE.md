# DocuSeal - Instalación de Servicio Windows

Guía completa para instalar y ejecutar DocuSeal como servicio de Windows usando los archivos ejecutables precompilados.

## Requisitos Previos

### Software Necesario
- **Windows 10/11** o **Windows Server 2016/2019/2022**
- **PostgreSQL 18+** instalado y ejecutándose
- **Wkhtmltopdf** instalado en la ruta predeterminada (`C:\Program Files\wkhtmltopdf\`)
- **Acceso administrativo** en la máquina

### Requerimientos del Equipo
- **Procesador**: Quad-core (4 núcleos), 2.0 GHz+
- **Memoria RAM**: 8 GB mínimo (16 GB recomendado)
- **Espacio en Disco**: 2 GB mínimo para el servicio
- **Conexión a Internet**: Estable (requerida para timbrado con PAC)

## Archivos Incluidos

En la carpeta `dist/` encontrarás:

```
dist/
├── DocuSealService.exe          ← Ejecutable del servicio
├── DocuSeal_Install.bat         ← Script de instalación
└── DocuSeal_Uninstall.bat       ← Script de desinstalación
```

## Paso 1: Configuración del Archivo `.env`

**Ubicación**: `C:\Users\<TuUsuario>\Desktop\DespliegueV2\DocuSeal-main\.env`

El archivo `.env` debe contener todas las credenciales necesarias. Usa el archivo `.env` existente en la raíz del proyecto como referencia.

### Variables Requeridas

```env
# ============================================
# Configuración de PostgreSQL
# ============================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=certificados_pac
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui
DB_SSL_MODE=prefer

# ============================================
# Configuración de Correo (Email Service)
# ============================================
EMAIL_SENDER=tu_email@dominio.com
EMAIL_PASSWORD=contraseña_app
EMAIL_SMTP_SERVER=mail.dominio.com
EMAIL_SMTP_PORT=465
EMAIL_USE_TLS=true
```

**Nota**: El `.env` debe estar en la **raíz del proyecto** para que el servicio pueda encontrarlo.

## Paso 2: Instalación del Servicio

### Instalación Rápida

1. **Abre el Explorador de Archivos** y navega a:
   ```
   C:\Users\<TuUsuario>\Desktop\DespliegueV2\DocuSeal-main\dist
   ```

2. **Haz clic derecho en `DocuSeal_Install.bat`** y selecciona **"Ejecutar como administrador"**

   El script hará automáticamente:
   - ✓ Descargar NSSM (gestor de servicios Windows)
   - ✓ Buscar el archivo `.env` en las ubicaciones esperadas
   - ✓ Crear el servicio "DocuSealService"
   - ✓ Configurar el servicio para reiniciarse automáticamente
   - ✓ Iniciar el servicio

3. **Verifica que el servicio inició correctamente** accediendo a:
   - http://localhost:8000/admin

## Paso 3: Verificar que el Servicio Está Activo

### Acceder a la Aplicación
- **Aplicación Web**: http://localhost:8000/admin
- **Service API**: http://localhost:8000/service
- **API Docs**: http://localhost:8000/service/docs


## Gestión del Servicio

### Detener el Servicio
```powershell
# Como Administrador
Stop-Service -Name DocuSealService
```

### Iniciar el Servicio
```powershell
# Como Administrador
Start-Service -Name DocuSealService
```

### Reiniciar el Servicio
```powershell
# Como Administrador
Restart-Service -Name DocuSealService
```

### Ver Logs del Servicio
Los logs se guardan en:
```
C:\Users\<TuUsuario>\AppData\Local\DocuSeal\logs\
```

Para ver los últimos logs:
```powershell
Get-Content "C:\Users\$env:USERNAME\AppData\Local\DocuSeal\logs\service.log" -Tail 50
```

## Desinstalación del Servicio

### Usando el Script de Desinstalación

1. **Abre el Explorador de Archivos** y navega a:
   ```
   C:\Users\<TuUsuario>\Desktop\DespliegueV2\DocuSeal-main\dist
   ```

2. **Haz clic derecho en `DocuSeal_Uninstall.bat`** y selecciona **"Ejecutar como administrador"**

El script hará automáticamente:
- ✓ Detener el servicio DocuSealService
- ✓ Eliminar el servicio de Windows
- ✓ Limpiar archivos temporales

## Actualizar el Servicio

Cuando hagas cambios al código:

1. **Detén el servicio**
   ```powershell
   Stop-Service -Name DocuSealService
   ```

2. **Desinstala el servicio**
   ```powershell
   cd "C:\Users\<TuUsuario>\Desktop\DespliegueV2\DocuSeal-main\dist"
   .\DocuSeal_Uninstall.bat
   ```

3. **Recompila el .exe** (desde la raíz del proyecto)
   ```powershell
   cd "C:\Users\<TuUsuario>\Desktop\DespliegueV2\DocuSeal-main"
   & ".\venv\Scripts\python.exe" -m PyInstaller DocuSealService.spec --distpath "dist" --workpath "build" --noconfirm
   ```

4. **Reinstala el servicio**
   ```powershell
   cd "C:\Users\<TuUsuario>\Desktop\DespliegueV2\DocuSeal-main\dist"
   .\DocuSeal_Install.bat
   ```

## Características del Servicio

✅ **Instalación Automática**: Descarga NSSM automáticamente
✅ **Auto-Reinicio**: Se reinicia automáticamente si falla
✅ **Logging**: Registra todas las actividades en `%APPDATA%\DocuSeal\logs\`
✅ **API REST**: Endpoints para sellado, timbrado y cancelación de CFDI
✅ **Frontend Incluido**: Interfaz web en `/admin`
✅ **Base de Datos**: Integración con PostgreSQL
✅ **Correo Automático**: Envío de comprobantes por email

## URLs de Acceso

| Componente | URL |
|-----------|-----|
| **Aplicación Web** | http://localhost:8000/admin |
| **API Service** | http://localhost:8000/service |
| **API Docs** | http://localhost:8000/service/docs |

---
