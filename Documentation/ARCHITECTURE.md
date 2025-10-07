# DocuSeal - Arquitectura Visual

## 🎯 Separación de APIs

```
┌─────────────────────────────────────────────────────────────────┐
│                        DOCUSEAL SYSTEM                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
        ┌───────▼────────┐          ┌───────▼────────┐
        │  SERVICE API   │          │   ADMIN API    │
        │  Puerto: 8000  │          │  Puerto: 8001  │
        │                │          │                │
        │  🌐 PÚBLICO    │          │  🔒 INTERNO    │
        └───────┬────────┘          └───────┬────────┘
                │                            │
                └─────────────┬──────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   BUSINESS LAYER   │
                    │   (Compartido)     │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │    DATA LAYER      │
                    │   (Compartido)     │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │ INFRASTRUCTURE     │
                    │   (Compartido)     │
                    └────────────────────┘
```

## 📦 Componentes del Sistema

### 1. SERVICE API (Puerto 8001)
**Propósito**: API pública para clientes externos

**Endpoints**:
- `POST /timbrar/` - Timbrar CFDI sellado
- `POST /sellar/` - Sellar CFDI
- `POST /timbrarSellar/` - Proceso completo
- `GET /health` - Health check

**Características**:
- Sin autenticación requerida
- CORS permisivo
- Documentación pública
- Ideal para integraciones

**Uso típico**:
```bash
curl -X POST http://localhost:8001/timbrar/ \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

### 2. ADMIN API (Puerto 8002)
**Propósito**: Panel administrativo para gestión interna

**Endpoints de Autenticación**:
- `POST /api/register` - Registro de usuarios
- `POST /api/login` - Login de usuarios

**Endpoints de Certificados**:
- `GET /api/v1/certificados/` - Listar todos
- `GET /api/v1/certificados/usuario/{usuario}` - Por usuario
- `GET /api/v1/certificados/numero/{numero}` - Por número
- `POST /api/v1/certificados/` - Crear
- `PUT /api/v1/certificados/{id}` - Actualizar
- `DELETE /api/v1/certificados/{id}` - Eliminar

**Características**:
- Autenticación futura con JWT
- CORS restrictivo
- Documentación administrativa
- Gestión de BD

**Uso típico**:
```bash
curl -X GET http://localhost:8002/api/v1/certificados/
```

---

### 3. BUSINESS LAYER (Compartido)
**Módulos principales**:

```
Business/
├── SellarXML.py             # Sellado digital de CFDI
├── Timbrado.py              # Integración con PAC
├── ValidadorCFDI.py         # Validación de comprobantes
├── ConfiguracionLogin.py    # Lógica de login
├── ConfiguracionRegistro.py # Lógica de registro
├── ConfiguracionCertificados.py # Gestión de certificados
├── ConfiguracionSello.py    # Configuración de sellado
├── Correo.py                # Envío de emails
├── PDF.py                   # Generación de PDFs
└── PreferenciasCliente.py   # Preferencias de usuario
```

---

### 4. DATA LAYER (Compartido)
**Módulos principales**:

```
Data/
├── cartaPorte.py        # Manejo de Carta Porte
├── ConvertirJson.py     # JSON → XML CFDI
└── InterpreteJson.py    # Interpretación de datos
```

---

### 5. INFRASTRUCTURE LAYER (Compartido)
**Módulos principales**:

```
Infraestructure/
├── PACClient.py         # Cliente HTTP para PAC
├── RespuestaSAT.py      # Parser de respuestas SAT
└── ConfiguracionPAC.py  # Configuración del PAC
```

---

### 6. DATABASE LAYER (Compartido)
**Módulos principales**:

```
DB/
├── DBManager.py         # Gestor principal de BD
├── settings.py          # Configuración de conexión
└── requirements.txt     # Dependencias de BD
```

---

## 🔄 Flujos de Trabajo

### Flujo 1: Timbrado desde Cliente Externo
```
Cliente Externo
    │
    │ POST /timbrarSellar/
    ▼
Service API (8001)
    │
    ├──▶ ConvertirJson (Data Layer)
    ├──▶ SellarXML (Business Layer)
    ├──▶ ValidadorCFDI (Business Layer)
    ├──▶ PACClient (Infrastructure Layer)
    └──▶ PDF (Business Layer)
    │
    ▼
Response: XML Timbrado + PDF
```

### Flujo 2: Gestión de Certificados desde Frontend
```
Frontend (index.html)
    │
    │ GET /api/v1/certificados/
    ▼
Admin API (8002)
    │
    └──▶ ConfiguracionCertificados (Business Layer)
            │
            └──▶ DBManager (DB Layer)
                    │
                    ▼
                Database
    │
    ▼
Response: Lista de certificados
```

### Flujo 3: Login de Usuario
```
Frontend (login.html)
    │
    │ POST /api/login
    ▼
Admin API (8002)
    │
    └──▶ ConfiguracionLogin (Business Layer)
            │
            └──▶ DBManager (DB Layer)
    │
    ▼
Response: Token + Datos de usuario
```

---

## 🚀 Scripts de Inicio

### start_service.ps1
```powershell
# Inicia SOLO Service API
cd backend/app/api_service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### start_admin.ps1
```powershell
# Inicia SOLO Admin API
cd backend/app/api_admin
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### start_all.ps1
```powershell
# Inicia AMBAS APIs simultáneamente
# Service en puerto 8001
# Admin en puerto 8002
```

---

## 📂 Estructura de Archivos Simplificada

```
DocuSeal/
│
├── start_service.ps1        ← Script Service API
├── start_admin.ps1          ← Script Admin API
├── start_all.ps1            ← Script Ambas APIs
├── README.md                ← Documentación completa
├── QUICKSTART.md            ← Guía rápida
│
├── backend/app/
│   │
│   ├── api_service/         ← SERVICE API (Puerto 8001)
│   │   └── main.py
│   │
│   ├── api_admin/           ← ADMIN API (Puerto 8002)
│   │   └── main.py
│   │
│   ├── Business/            ← Lógica compartida
│   ├── Data/                ← Datos compartidos
│   ├── DB/                  ← Base de datos
│   ├── Infraestructure/     ← Infraestructura
│   └── ejemplos/            ← JSONs de ejemplo
│
└── Frontend/                ← Panel web (conecta a Admin API)
    ├── index.html
    ├── login.html
    ├── js/api.js            ← Configurado para puerto 8002
    └── css/
```

---

## 🎨 Diferencias Clave

| Aspecto | SERVICE API (8001) | ADMIN API (8002) |
|---------|-------------------|------------------|
| **Propósito** | Servicios públicos | Gestión interna |
| **Clientes** | Externos | Frontend web |
| **Autenticación** | No requerida | Futura con JWT |
| **CORS** | Permisivo (*) | Restrictivo |
| **Endpoints** | 4 (health + 3 servicios) | 9 (auth + certificados) |
| **Deploy** | Producción pública | Red interna |
| **Documentación** | Pública | Privada |

---

## 🔐 Seguridad por Capas

### Capa 1: Separación de APIs
- ✅ Service y Admin en puertos diferentes
- ✅ Sin exposición de endpoints administrativos en Service

### Capa 2: CORS
- ✅ Service API: Permisivo (público)
- ✅ Admin API: Restrictivo (solo frontend autorizado)

### Capa 3: Autenticación (Futuro)
- ⏳ JWT tokens para Admin API
- ⏳ Rate limiting en Service API
- ⏳ API Keys para clientes externos

### Capa 4: Encriptación
- ✅ Contraseñas encriptadas con Fernet
- ✅ Certificados almacenados de forma segura
- ✅ Comunicación HTTPS con PAC

---

## 📊 Métricas del Sistema

### Rendimiento
- **Service API**: Optimizada para alto volumen de requests
- **Admin API**: Optimizada para operaciones CRUD

### Escalabilidad
- APIs independientes = escalado independiente
- Business Layer compartido = sin duplicación de código

### Mantenibilidad
- Separación clara de responsabilidades
- Código modular y reutilizable
- Documentación automática con Swagger

---

## 🎯 Casos de Uso

### Caso 1: Empresa Externa
```
Empresa con sistema ERP
    ↓
Integra con Service API (8001)
    ↓
Genera facturas automáticamente
```

### Caso 2: Administrador Interno
```
Administrador
    ↓
Accede al Frontend
    ↓
Gestiona certificados vía Admin API (8002)
    ↓
Certificados disponibles para Service API
```

### Caso 3: Desarrollador
```
Desarrollador
    ↓
Consulta Swagger docs (/docs)
    ↓
Prueba endpoints directamente
    ↓
Integra en su aplicación
```

---

**Última actualización**: 2 de Octubre de 2025
