# DocuSeal - Sistema de Sellado y Timbrado de CFDI

Sistema completo para el sellado y timbrado de Comprobantes Fiscales Digitales por Internet (CFDI) en México.

## Requisitos del Sistema

### Software Necesario

Python 3.10.x (Deseable): https://www.python.org/downloads/
Node 22.x (Deseable): https://nodejs.org/en/download
PostgreSQL 18 (Deseable): https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
Git(opcional, para clonar el repositorio): https://git-scm.com/install/windows
Wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
   Nota: descargar en la ruta predeterminada que marca el instalador

### Sistema Operativo
- Windows 10/11 (con PowerShell)
- Windows Server 2016/2019/2022 (recomendado)
- Linux (Ubuntu 20.04+, Debian 10+)

### Requerimientos del equipo

   #### Windows (10/11)
   - **Procesador**: Quad-core (4 núcleos), 2.0 GHz+
   - **Memoria RAM**: 8 GB mínimo (16 GB recomendado)
   - **Espacio en Disco**: 15 GB de espacio libre o superior
   - **Conexión a Internet**: Estable (requerida para timbrado con PAC)

   #### Windows Server
   - **Procesador**: Hexa-core (6 núcleos) o superior, 2.5 GHz+
   - **Memoria RAM**: 16 GB mínimo (32 GB recomendado para alta concurrencia)
   - **Espacio en Disco**: 50 GB de espacio libre o superior (SSD recomendado)
   - **Conexión a Internet**: Dedicada y estable con ancho de banda adecuado

   #### Linux
   - **Procesador**: Quad-core (4 núcleos) o superior, 2.0 GHz+
   - **Memoria RAM**: 8 GB mínimo (16 GB recomendado)
   - **Espacio en Disco**: 15 GB de espacio libre o superior(50 GB para producción)
   - **Conexión a Internet**: Estable (requerida para timbrado con PAC)

   **Nota**: Para un entorno de producción con 100 peticiones cada 20 minutos, se recomienda Windows Server con la configuración superior

## Instalación

1. Clonar o Descargar el Proyecto

```bash
git clone https://github.com/Habib398/DocuSeal-main.git
cd DocuSeal
```

O descargar y extraer el archivo ZIP del proyecto.


2. Configurar la Base de Datos (Aun en actualización)
   1. Crear la Base de Datos en PostgreSQL
   Abrir pgAdmin o usar la terminal de PostgreSQL:

```sql
CREATE DATABASE certificados_pac;
```

   2. Crear las Tablas
   Conectarse a la base de datos y ejecutar:

```sql
CREATE TABLE certificados_pac (
    id SERIAL PRIMARY KEY,
    usuarioPAC VARCHAR(255) NOT NULL,
    contrasenaPAC VARCHAR(255) NOT NULL,
    nombreEmpresa VARCHAR(255) NOT NULL,
    CER BYTEA,
    KEY BYTEA,
    vigencia VARCHAR(100),
    noCertificado VARCHAR(100),
    Certificado TEXT,
    pwdCER VARCHAR(255),
    correo VARCHAR(255),
    telefono VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    verificacion BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
   3. Configurar Variables de Entorno
   Crear el archivo `.env` en la carpeta `backend/app/DB/`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=certificados_pac
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui
DB_SSL_MODE=prefer
```
Reemplazar con los valores de configuración de postsgre asignados.

3. Instalar Dependencias

   ## Instalación Automatizada ()
   
   ### En Windows (PowerShell):
   ```powershell
   # Desde la raíz del proyecto
   .\Scripts\install_dependencies.ps1
   ```
   
   ### En Linux:
   ```bash
   # Desde la raíz del proyecto
   chmod +x Scripts/install_dependencies.sh
   ./Scripts/install_dependencies.sh
   ```

   El script instalará automáticamente todas las dependencias de backend y frontend.

4. Ejecutar el Proyecto

   ## Modo de Ejecución
   Desde la raíz del proyecto en Windows:

   ```powershell
   .\Scripts\start_DocuSeal.ps1
   ```
   
   ### URLs de Acceso:
   - **Aplicación Web**: http://localhost:8000/admin
   - **Service API**: http://localhost:8000/service
   - **Service API Docs**: http://localhost:8000/service/docs

   ## Modo de Desarrollo (Si se requiere)
   Si necesitas trabajar con el frontend o backend por separado:

   ### Terminal 1 - Backend:
   ```powershell
   # Navegar a la raíz del proyecto
   cd backend/app
   
   # Activar entorno virtual (si existe)
   .\.venv\Scripts\Activate.ps1
   
   # Iniciar servidor unificado
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   ### Terminal 2 - Frontend:
   ```bash
   cd Frontend/react-app
   npm run dev
   ```
   En este modo, el frontend estará disponible en http://localhost:3000

6. Documentación Adicional

- **Arquitectura del Sistema**: Ver `Documentation/ARCHITECTURE.md`
- **Base de Datos**: Ver `Documentation/Database.md`
- **Ejemplos de Uso**: Revisar carpeta `ejemplos/`
