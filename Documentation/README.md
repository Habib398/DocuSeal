# DocuSeal 🔐

Sistema completo para sellado y timbrado de CFDI (Comprobantes Fiscales Digitales por Internet) con gestión administrativa integrada.

## 📋 Tabla de Contenidos

- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Componentes Principales](#componentes-principales)
- [APIs y Endpoints](#apis-y-endpoints)
- [Instalación y Configuración](#instalación-y-configuración)
- [Uso](#uso)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)

---

## 🏗️ Arquitectura del Sistema

DocuSeal está diseñado con una **arquitectura separada** que distingue entre servicios públicos y administración:

```
┌─────────────────────────────────────────────────────────────┐
│                      DocuSeal System                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────┐        ┌──────────────────────┐   │
│  │   Service API       │        │     Admin API        │   │
│  │   Puerto: 8001      │        │   Puerto: 8002       │   │
│  ├─────────────────────┤        ├──────────────────────┤   │
│  │ • /timbrar          │        │ • /api/register      │   │
│  │ • /sellar           │        │ • /api/login         │   │
│  │ • /timbrarSellar    │        │ • /api/v1/cert...*   │   │
│  │ • /health           │        │ • /health            │   │
│  └─────────┬───────────┘        └──────────┬───────────┘   │
│            │                               │                │
│            └───────────┬───────────────────┘                │
│                        │                                     │
│            ┌───────────▼───────────┐                        │
│            │   Business Layer      │                        │
│            │   • SellarXML         │                        │
│            │   • Timbrado          │                        │
│            │   • Configuraciones   │                        │
│            │   • Validadores       │                        │
│            └───────────┬───────────┘                        │
│                        │                                     │
│            ┌───────────▼───────────┐                        │
│            │   Data Layer          │                        │
│            │   • DBManager         │                        │
│            │   • ConvertirJson     │                        │
│            │   • InterpreteJson    │                        │
│            └───────────┬───────────┘                        │
│                        │                                     │
│            ┌───────────▼───────────┐                        │
│            │   Infrastructure      │                        │
│            │   • PACClient         │                        │
│            │   • RespuestaSAT      │                        │
│            └───────────────────────┘                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         │                                  │
         │                                  │
    Clientes                          Frontend Web
    Externos                       (Panel Administrativo)
```

### Separación de Responsabilidades

1. **Service API (Puerto 8001)** - API Pública
   - Servicios de sellado y timbrado de CFDI
   - Accesible para clientes externos sin autenticación
   - Endpoints RESTful para integración con sistemas externos
   - Ideal para ambientes productivos

2. **Admin API (Puerto 8002)** - API Administrativa
   - Gestión de usuarios y certificados
   - Interfaz para el panel administrativo web
   - Preparado para autenticación futura
   - Solo para uso interno

---

## 📁 Estructura del Proyecto

```
DocuSeal/
│
├── backend/
│   └── app/
│       ├── api_service/              # API Pública (Puerto 8001)
│       │   └── main.py               # Endpoints de sellado/timbrado
│       │
│       ├── api_admin/                # API Administrativa (Puerto 8002)
│       │   └── main.py               # Endpoints de gestión
│       │
│       ├── Business/                 # Lógica de Negocio (Compartida)
│       │   ├── SellarXML.py          # Sellado de CFDI
│       │   ├── Timbrado.py           # Timbrado con PAC
│       │   ├── ValidadorCFDI.py      # Validación de comprobantes
│       │   ├── ConfiguracionLogin.py
│       │   ├── ConfiguracionRegistro.py
│       │   ├── ConfiguracionCertificados.py
│       │   ├── ConfiguracionSello.py
│       │   ├── Correo.py
│       │   ├── PDF.py
│       │   └── PreferenciasCliente.py
│       │
│       ├── Data/                     # Capa de Datos (Compartida)
│       │   ├── cartaPorte.py         # Manejo de Carta Porte
│       │   ├── ConvertirJson.py      # Conversión JSON → XML
│       │   └── InterpreteJson.py     # Interpretación de datos
│       │
│       ├── DB/                       # Gestión de Base de Datos
│       │   ├── DBManager.py          # Administrador de BD
│       │   ├── settings.py           # Configuración de BD
│       │   └── requirements.txt
│       │
│       ├── Infraestructure/          # Infraestructura Externa
│       │   ├── PACClient.py          # Cliente para PAC
│       │   ├── RespuestaSAT.py       # Procesamiento respuestas SAT
│       │   └── ConfiguracionPAC.py
│       │
│       ├── Presentation/             # [DEPRECADO - Ver api_service y api_admin]
│       │   └── main.py               # Archivo original unificado
│       │
│       └── ejemplos/                 # Ejemplos de uso
│           ├── endpoint_sellar_ejemplo.json
│           ├── endpoint_timbrar_ejemplo.json
│           ├── endpoint_timbrarSellar_ejemplo.json
│           ├── endpoint_timbrarSellar_xml_string_ejemplo.json
│           └── factura_carta_porte_ejemplo.json
│
├── Frontend/                         # Panel Administrativo Web
│   ├── index.html                    # Dashboard principal
│   ├── login.html                    # Página de login
│   ├── css/
│   │   ├── styles.css
│   │   └── login.css
│   └── js/
│       ├── api.js                    # Cliente API (conecta a Admin API)
│       └── main.js                   # Lógica del frontend
│
├── Temp/                             # Archivos temporales
│   ├── contraseña.txt
│   └── CSD PRUEBA/                   # Certificados de prueba
│       ├── AAA010101AAA.cer
│       └── AAA010101AAA.key
│
├── start_service.ps1                 # Iniciar Service API
├── start_admin.ps1                   # Iniciar Admin API
├── start_all.ps1                     # Iniciar ambas APIs
└── README.md                         # Este archivo
```

---

## 🧩 Componentes Principales

### 1. Business Layer (Lógica de Negocio)

#### SellarXML.py
- Genera el sello digital del CFDI
- Calcula la cadena original
- Aplica el algoritmo de sellado con certificados CSD

#### Timbrado.py
- Integración con PAC (Proveedor Autorizado de Certificación)
- Envía CFDI sellado para obtener timbre fiscal
- Procesa respuestas del SAT

#### ValidadorCFDI.py
- Valida estructura y contenido de CFDI
- Verifica cumplimiento con reglas del SAT
- Validación de sellos y timbres

#### ConfiguracionCertificados.py
- CRUD de certificados digitales
- Gestión de archivos .cer y .key
- Validación y almacenamiento de credenciales

### 2. Data Layer (Capa de Datos)

#### DBManager.py
- Conexión y manejo de base de datos
- Operaciones CRUD genéricas
- Gestión de transacciones

#### ConvertirJson.py
- Conversión de datos JSON a XML CFDI
- Aplicación de estructura SAT oficial
- Validación de datos de entrada

#### InterpreteJson.py
- Lectura y procesamiento de JSON
- Extracción de datos para CFDI
- Validación de formato

### 3. Infrastructure Layer

#### PACClient.py
- Cliente HTTP para comunicación con PAC
- Manejo de autenticación
- Procesamiento de respuestas

#### RespuestaSAT.py
- Parser de respuestas XML del SAT
- Extracción de UUID y datos de timbrado
- Manejo de errores del SAT

---

## 🌐 APIs y Endpoints

### Service API - Puerto 8001 (API Pública)

**Base URL:** `http://localhost:8001`

#### Endpoints Disponibles:

##### 1. Health Check
```http
GET /health
```
Verifica el estado del servicio.

**Respuesta:**
```json
{
  "status": "ok",
  "message": "DocuSeal Service API is running"
}
```

##### 2. Sellar CFDI
```http
POST /sellar/
Content-Type: application/json

{
  "Emisor": { ... },
  "Receptor": { ... },
  "Conceptos": [ ... ],
  "certificados": {
    "ruta_cer": "path/to/cert.cer",
    "ruta_key": "path/to/key.key",
    "contrasena": "password"
  }
}
```

**Respuesta:**
```json
{
  "xml_con_sello": "<cfdi:Comprobante ... />",
  "sello": "base64_encoded_seal...",
  "cadena_original": "||fields|separated|by|pipes||"
}
```

##### 3. Timbrar CFDI
```http
POST /timbrar/
Content-Type: application/json

{
  "xml": "<cfdi:Comprobante ... />",
  "usuario_pac": "usuario",
  "contrasena_pac": "password",
  "pruebas": true
}
```

**Respuesta:**
```json
{
  "uuid": "12345678-1234-1234-1234-123456789012",
  "fecha_timbrado": "2025-10-02T12:00:00",
  "xml_timbrado": "<cfdi:Comprobante ... />",
  "mensaje": "Timbrado exitoso"
}
```

##### 4. Sellar y Timbrar (Proceso Completo)
```http
POST /timbrarSellar/
Content-Type: application/json

{
  "Emisor": { ... },
  "Receptor": { ... },
  "Conceptos": [ ... ],
  "certificados": { ... },
  "PAC": {
    "usuario": "usuario_pac",
    "contrasena": "password_pac"
  },
  "pruebas": true
}
```

**Respuesta:**
```json
{
  "uuid": "12345678-1234-1234-1234-123456789012",
  "fecha_timbrado": "2025-10-02T12:00:00",
  "xml_timbrado": "<cfdi:Comprobante ... />",
  "pdf": "base64_encoded_pdf...",
  "mensaje": "Proceso completado exitosamente"
}
```

---

### Admin API - Puerto 8002 (API Administrativa)

**Base URL:** `http://localhost:8002`

#### Endpoints Disponibles:

##### Autenticación

###### 1. Registrar Usuario
```http
POST /api/register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "confirm_password": "password123",
  "nombre": "Nombre Usuario"
}
```

###### 2. Login
```http
POST /api/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

##### Gestión de Certificados

###### 3. Listar Todos los Certificados
```http
GET /api/v1/certificados/
```

###### 4. Obtener Certificado por Usuario PAC
```http
GET /api/v1/certificados/usuario/{usuario_pac}
```

###### 5. Obtener Certificado por Número
```http
GET /api/v1/certificados/numero/{no_certificado}
```

###### 6. Crear Certificado
```http
POST /api/v1/certificados/
Content-Type: application/json

{
  "usuario_pac": "usuario",
  "no_certificado": "20001000000300022323",
  "ruta_cer": "path/to/cert.cer",
  "ruta_key": "path/to/key.key",
  "contrasena": "encrypted_password"
}
```

###### 7. Actualizar Certificado
```http
PUT /api/v1/certificados/{cert_id}
Content-Type: application/json

{
  "usuario_pac": "usuario_actualizado",
  ...
}
```

###### 8. Eliminar Certificado
```http
DELETE /api/v1/certificados/{cert_id}
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Python 3.10+**
- **pip** (gestor de paquetes Python)
- **PostgreSQL** o **SQLite** (para base de datos)
- **uvicorn** (servidor ASGI)

### Instalación de Dependencias

```powershell
# Navegar al directorio del proyecto
cd DocuSeal

# Instalar dependencias de la API
pip install fastapi uvicorn sqlalchemy psycopg2-binary cryptography reportlab

# O usar requirements.txt si existe
pip install -r backend/app/requirements.txt
pip install -r backend/app/DB/requirements.txt
```

### Configuración de Base de Datos

Editar `backend/app/DB/settings.py` con tus credenciales:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'docuseal_db',
    'user': 'tu_usuario',
    'password': 'tu_password',
    'port': 5432
}
```

### Configuración de Certificados

Colocar tus certificados CSD en una ubicación segura y actualizar las rutas en la base de datos o en los requests JSON.

---

## 💻 Uso

### Opción 1: Iniciar Ambas APIs Simultáneamente

```powershell
.\start_all.ps1
```

Esto iniciará:
- **Service API** en `http://localhost:8001`
- **Admin API** en `http://localhost:8002`

### Opción 2: Iniciar APIs Por Separado

#### Iniciar solo Service API:
```powershell
.\start_service.ps1
```

#### Iniciar solo Admin API:
```powershell
.\start_admin.ps1
```

### Documentación Interactiva (Swagger UI)

Una vez iniciados los servicios, accede a la documentación automática:

- **Service API**: http://localhost:8001/docs
- **Admin API**: http://localhost:8002/docs

### Frontend Web (Panel Administrativo)

Abrir en un navegador:
```
file:///C:/Users/Abitt/OneDrive/Escritorio/DocuSealV2/DocuSeal/Frontend/index.html
```

O servir con un servidor web local:
```powershell
cd Frontend
python -m http.server 8080
```

Luego acceder a: `http://localhost:8080`

---

## 🔧 Ejemplos de Uso

### Ejemplo 1: Sellar un CFDI

```python
import requests
import json

url = "http://localhost:8001/sellar/"

data = {
    "Emisor": {
        "Rfc": "AAA010101AAA",
        "Nombre": "Empresa Ejemplo",
        "RegimenFiscal": "601"
    },
    "Receptor": {
        "Rfc": "XAXX010101000",
        "Nombre": "Cliente Ejemplo",
        "UsoCFDI": "G03"
    },
    "Conceptos": [
        {
            "ClaveProdServ": "01010101",
            "NoIdentificacion": "001",
            "Cantidad": "1",
            "ClaveUnidad": "E48",
            "Unidad": "Unidad",
            "Descripcion": "Producto de ejemplo",
            "ValorUnitario": "1000.00",
            "Importe": "1000.00"
        }
    ],
    "certificados": {
        "ruta_cer": "C:/ruta/certificado.cer",
        "ruta_key": "C:/ruta/llave.key",
        "contrasena": "password123"
    }
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

### Ejemplo 2: Timbrar y Sellar (Proceso Completo)

```python
import requests
import json

url = "http://localhost:8001/timbrarSellar/"

data = {
    # ... mismo data del ejemplo 1 ...
    "PAC": {
        "usuario": "usuario_pac",
        "contrasena": "password_pac"
    },
    "pruebas": True
}

response = requests.post(url, json=data)
result = response.json()

# Guardar XML timbrado
with open("cfdi_timbrado.xml", "w", encoding="utf-8") as f:
    f.write(result["xml_timbrado"])

print(f"UUID: {result['uuid']}")
print(f"Fecha: {result['fecha_timbrado']}")
```

### Ejemplo 3: Gestión de Certificados desde Admin API

```python
import requests

# Login
login_url = "http://localhost:8002/api/login"
login_data = {
    "email": "admin@ejemplo.com",
    "password": "admin123"
}
session = requests.post(login_url, json=login_data).json()
token = session.get("token")

# Listar certificados
cert_url = "http://localhost:8002/api/v1/certificados/"
headers = {"Authorization": f"Bearer {token}"}  # Cuando se implemente auth
response = requests.get(cert_url, headers=headers)
print(response.json())
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **SQLAlchemy** - ORM para manejo de base de datos
- **Cryptography** - Manejo de certificados y encriptación
- **ReportLab** - Generación de PDFs
- **lxml** - Procesamiento de XML

### Frontend
- **HTML5/CSS3** - Interfaz de usuario
- **JavaScript (Vanilla)** - Lógica del cliente
- **Fetch API** - Comunicación con backend

### Base de Datos
- **PostgreSQL** / **SQLite** - Almacenamiento de datos

### Seguridad
- **Fernet** - Encriptación simétrica de contraseñas
- **SSL/TLS** - Comunicación segura con PAC

---

## 📊 Flujo de Trabajo

### Proceso de Sellado y Timbrado

```
1. Cliente envía datos JSON
         ↓
2. API Service recibe request
         ↓
3. ConvertirJson → XML CFDI
         ↓
4. SellarXML → Genera sello digital
         ↓
5. ValidadorCFDI → Valida estructura
         ↓
6. PACClient → Envía a timbrar
         ↓
7. SAT → Retorna UUID y timbre
         ↓
8. RespuestaSAT → Procesa respuesta
         ↓
9. PDF.py → Genera representación impresa
         ↓
10. API retorna XML timbrado + PDF
```

### Gestión Administrativa

```
1. Usuario accede al Frontend
         ↓
2. Login → Admin API valida credenciales
         ↓
3. Frontend consulta certificados
         ↓
4. Admin API → DBManager → BD
         ↓
5. Usuario crea/edita/elimina certificados
         ↓
6. Cambios se reflejan en BD
         ↓
7. Certificados disponibles para Service API
```

---

## 🔐 Seguridad

### Mejores Prácticas Implementadas

1. **Separación de APIs**: Servicios públicos y administrativos separados
2. **Encriptación de contraseñas**: Usando Fernet encryption
3. **Validación de entrada**: En todos los endpoints
4. **CORS configurado**: Políticas específicas por API
5. **Health checks**: Monitoreo de disponibilidad

### Recomendaciones Futuras

- [ ] Implementar JWT para autenticación en Admin API
- [ ] Agregar rate limiting en Service API
- [ ] Habilitar HTTPS en producción
- [ ] Implementar logs de auditoría
- [ ] Agregar 2FA para administradores

---

## 📝 Notas Adicionales

### Archivo Deprecado

El archivo `backend/app/Presentation/main.py` es la versión original que unificaba ambas APIs. Ha sido reemplazado por:
- `backend/app/api_service/main.py` (Service API)
- `backend/app/api_admin/main.py` (Admin API)

Se mantiene por compatibilidad pero **no se recomienda su uso**.

### Certificados de Prueba

Los certificados en `Temp/CSD PRUEBA/` son para testing y están disponibles públicamente por el SAT. **NO usar en producción**.

### Ejemplos

La carpeta `backend/app/ejemplos/` contiene JSONs de ejemplo para probar los endpoints. Consultar `ejemplos/README.md` para más detalles.

---

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/NuevaFuncionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Abre un Pull Request

---

## 📞 Soporte

Para preguntas o problemas:
- Abrir un issue en GitHub
- Consultar la documentación Swagger de cada API
- Revisar los ejemplos en `backend/app/ejemplos/`

---

## 📄 Licencia

[Especificar licencia del proyecto]

---

## 🎯 Roadmap

### Versión Actual (1.0.0)
- ✅ API de sellado y timbrado funcional
- ✅ Panel administrativo web
- ✅ Gestión de certificados
- ✅ Separación Service/Admin APIs

### Próximas Versiones

#### v1.1.0
- [ ] Autenticación JWT en Admin API
- [ ] Soporte para Carta Porte 3.0
- [ ] Generación de reportes

#### v1.2.0
- [ ] API de cancelación de CFDI
- [ ] Dashboard con estadísticas
- [ ] Notificaciones por email

#### v2.0.0
- [ ] Soporte para múltiples PACs
- [ ] Webhooks para eventos
- [ ] SDK para clientes en múltiples lenguajes

---

**Desarrollado con ❤️ para simplificar la facturación electrónica en México**
