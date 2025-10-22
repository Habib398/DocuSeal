# DocuSeal - Sistema de Sellado y Timbrado de CFDI

Sistema completo para el sellado y timbrado de Comprobantes Fiscales Digitales por Internet (CFDI) en México.

## Requisitos del Sistema

### Software Necesario

Python 3.8 (Deseable)
Node.js 16.x (Deseable)
PostgreSQL 12 (Deseable)
Git(opcional, para clonar el repositorio)

### Sistema Operativo
Windows 10/11 (con PowerShell)
Linux (Ubuntu 20.04+, Debian 10+)
macOS 10.15+

### Requerimientos del equipo
   # Windows
   # Linux 

## Instalación

1. Clonar o Descargar el Proyecto

```bash
git clone https://github.com/Habib398/DocuSeal.git
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

3. Instalar Dependencias del Backend (Python)

   1. En Windows (PowerShell):

   ```powershell
   # Navegar a la carpeta del backend
   cd backend\app

   # Crear entorno virtual (recomendado)
   python -m venv venv

   # Activar entorno virtual
   .\venv\Scripts\Activate.ps1

   # Instalar dependencias
   pip install -r requirements.txt
   ```

   2. En Linux/macOS:
   ```bash
   # Navegar a la carpeta del backend
   cd backend/app

   # Crear entorno virtual
   python3 -m venv venv

   # Activar entorno virtual
   source venv/bin/activate

   # Instalar dependencias
   pip install -r requirements.txt
   ```

   3. Dependencias principales incluidas:
   - FastAPI - Framework web
   - Uvicorn - Servidor ASGI
   - psycopg2-binary - Conector PostgreSQL
   - bcrypt - Encriptación de contraseñas
   - pydantic - Validación de datos
   - python-dotenv - Gestión de variables de entorno

4. Instalar Dependencias del Frontend (React)

```bash
# Navegar a la carpeta del frontend
cd Frontend/react-app

# Instalar dependencias con npm
npm install

# O usar yarn si lo prefieres
# yarn install
```
5.  Ejecutar el Proyecto

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
