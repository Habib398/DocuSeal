# DocuSeal - Arquitectura Visual

## Arquitectura de Capas (4 Capas)

DocuSeal implementa una **arquitectura en capas (N-Tier Architecture)** simplificada que separa las responsabilidades del sistema en **4 capas independientes y reutilizables**. Esta arquitectura promueve la modularidad, mantenibilidad y escalabilidad del sistema.

### Capas del Sistema

1. **Presentation Layer** - APIs de exposición (Service API + Admin API)
2. **Business Layer** - Lógica de negocio y servicios externos
3. **Data Layer** - Transformación y estructuración de datos
4. **Database Layer** - Persistencia de datos

### Principios de la Arquitectura de Capas

1. **Separación de Responsabilidades**: Cada capa tiene una función específica y bien definida
2. **Bajo Acoplamiento**: Las capas son independientes entre sí
3. **Alta Cohesión**: Cada capa agrupa funcionalidades relacionadas
4. **Reutilización**: Las capas inferiores son compartidas por ambas APIs
5. **Flujo Unidireccional**: Las capas superiores dependen de las inferiores, nunca al revés

---

## Diagrama Completo de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  DOCUSEAL SYSTEM                                        │
│                           Arquitectura en Capas (N-Tier)                                │
│                         Sistema de Facturación Electrónica CFDI                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
                        ┌───────────────────┴─────────────────┐
                        │                                     │
       ┌────────────────▼───────────────┐   ┌─────────────────▼───────────┐
       │                                │   │                             │
       │      SERVICE API               │   │      ADMIN API              │
       │      (FastAPI)                 │   │      (FastAPI)              │
       │      Puerto: 8001              │   │      Puerto: 8002           │
       │                                │   │                             │
       │  Endpoints Públicos:           │   │  Endpoints Internos:        │
       │  ┌─────────────────────────┐   │   │  ┌──────────────────────┐   │
       │  │ POST /timbrar           │   │   │  │ POST /api/login      │   │
       │  │ POST /sellar            │   │   │  │ POST /api/register   │   │
       │  │ POST /timbrarSellar     │   │   │  │ GET /api/v1/certs    │   │
       │  │ POST /cancelar          │   │   │  │ POST /api/v1/cert    │   │
       │  │ POST /status            │   │   │  │ PUT /api/v1/cert/:id │   │
       │  │ POST /procesar          │   │   │  │ DEL /api/v1/cert/:id │   │
       │  │ GET  /health            │   │   │  │ GET /api/v1/prefs    │   │
       │  └─────────────────────────┘   │   │  │ PUT /api/v1/prefs    │   │
       │                                │   │  └──────────────────────┘   │
       └───────────┬────────────────────┘   └──────────┬──────────────────┘
                    │                                    │
                    │                                    │
┌───────────────────┴────────────────────────────────────┴───────────────────────────────┐
│                                                                                        │
│                         CAPA 1: PRESENTATION LAYER                                     │
│                            (Exposición de Servicios)                                   │
│                                                                                        │
│  • Validación de Entradas         • Manejo de CORS         • Documentación Swagger     │
│  • Serialización JSON              • Autenticación JWT      • Manejo de Errores        │
│                                                                                        │
└────────────────────────────────────┬───────────────────────────────────────────────────┘
                                     │
                                     │ Invoca servicios
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                         CAPA 2: BUSINESS LAYER                                      │
│                      (Lógica de Negocio y Orquestación)                             │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  Servicios Principales:                                                     │    │
│  │                                                                             │    │
│  │  • SellarXML.py              → Sellado digital con CSD                      │    │
│  │  • Timbrado.py               → Timbrado con PAC (Multi-PAC)                 │    │
│  │  • Cancelacion.py            → Cancelación de CFDI                          │    │
│  │  • ValidadorCFDI.py          → Validación de estructura SAT                 │    │
│  │  • StatusComprobante.py      → Consulta de estatus                          │    │
│  │  • PDF.py                    → Generación de representación impresa         │    │
│  │  • Correo.py                 → Envío de correos electrónicos                │    │
│  │  • PreferenciasCliente.py    → Gestión de preferencias                      │    │
│  │  • ResultadoTimbrado.py      → Procesamiento de respuestas PAC              │    │
│  │  • ResultadoCancelacion.py   → Procesamiento de cancelaciones               │    │
│  │                                                                             │    │
│  │  CFDI (Generación de Comprobantes):                                         │    │
│  │                                                                             │    │
│  │  • ComprobanteFactory.py     → Factory de comprobantes                      │    │
│  │  • ConvertirJson.py          → JSON → XML CFDI                              │    │
│  │  • Comprobantes/             → Ingreso, Egreso, Traslado, Pago, Nómina      │    │
│  │  • Complementos/             → Carta Porte, Pagos, etc.                     │    │
│  │                                                                             │    │
│  │  Configuration (Configuración y Seguridad):                                 │    │
│  │                                                                             │    │
│  │  • ConfiguracionLogin.py     → Autenticación de usuarios                    │    │
│  │  • ConfiguracionRegistro.py  → Registro y validación                        │    │
│  │  • ConfiguracionCertificados.py → Gestión de CSD (.cer/.key)                │    │
│  │  • ConfiguracionSello.py     → Configuración de sellado                     │    │
│  │                                                                             │    │
│  │  Services (Integración Externa):                                            │    │
│  │                                                                             │    │
│  │  • ServicioTimbrado.py       → Comunicación con PAC                         │    │
│  │  • ServicioCancelacion.py    → Cancelación vía PAC                          │    │
│  │  • ServicioSellado.py        → Proceso de sellado                           │    │
│  │  • ServiceStatusComprobante.py → Consulta de estatus                        │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└────────────────────────────────────┬────────────────────────────────────────────────┘
                                     │
                                     │ Transforma datos
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│                         CAPA 3: DATA LAYER                                           │
│                   (Transformación y Estructuración de Datos)                         │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐     │
│  │                                                                             │     │
│  │  • ConvertirJson.py          → Conversión JSON a XML CFDI 4.0               │     │
│  │  • InterpreteJson.py         → Interpretación y validación de JSON          │     │
│  │  • cartaPorte.py             → Manejo de complemento Carta Porte 3.0        │     │
│  │  • matriz_errores.txt        → Catálogo de errores estandarizados           │     │
│  │                                                                             │     │
│  │  Funciones:                                                                 │     │
│  │  Validación de esquemas    Mapeo de objetos                                 │     │
│  │  Generación XML SAT        Transformación de formatos                       │     │
│  │                                                                             │     │
│  └─────────────────────────────────────────────────────────────────────────────┘     │
│                                                                                      │
└────────────────────────────────────┬─────────────────────────────────────────────────┘
                                     │
                                     │ Persiste información
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│                         CAPA 4: DATABASE LAYER                                       │
│                          (Persistencia de Datos)                                     │
│                                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐    │
│  │                                                                              │    │
│  │  • DBManager.py              → CRUD y gestión de conexiones                  │    │
│  │  • settings.py               → Configuración de PostgreSQL                   │    │
│  │                                                                              │    │
│  │  Base de Datos: PostgreSQL 12+                                               │    │
│  │                                                                              │    │
│  │  Tablas principales:                                                         │    │
│  │  ┌──────────────────────────────────────────────────────────────┐            │    │
│  │  │  • usuarios          → Datos de clientes registrados         │            │    │
│  │  │  • certificados      → CSD almacenados (encriptados)         │            │    │
│  │  │  • preferencias      → Configuraciones de cliente            │            │    │
│  │  │  • comprobantes      → Histórico de CFDIs generados          │            │    │
│  │  │  • logs              → Auditoría y trazabilidad              │            │    │
│  │  └──────────────────────────────────────────────────────────────┘            │    │
│  │                                                                              │    │
│  │  Características:                                                            │    │
│  │  Connection Pooling        Soft Delete                                       │    │
│  │  Transacciones ACID         Migraciones de esquema                           │    │
│  │                                                                              │    │
│  └──────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Descripción Detallada de Capas

### Capa 1: PRESENTATION LAYER (Capa de Presentación)
**Responsabilidad**: Exponer funcionalidades del sistema a través de APIs REST

**Componentes**:
- **Service API** (Puerto 8001): API pública para clientes externos
- **Admin API** (Puerto 8002): API administrativa para gestión interna

**Características**:
- ✅ Manejo de peticiones HTTP
- ✅ Validación de entrada
- ✅ Serialización/Deserialización JSON
- ✅ Documentación automática (Swagger)
- ✅ Manejo de CORS
- ✅ Rate limiting (futuro)

**Ubicación**: `backend/app/api_service/` y `backend/app/api_admin/`

---

### Capa 2: BUSINESS LAYER (Capa de Lógica de Negocio)
**Responsabilidad**: Contener toda la lógica de negocio, reglas del dominio y comunicación con servicios externos

**Componentes principales**:
```
Business/
├── SellarXML.py              # Sellado digital de comprobantes
├── Timbrado.py               # Proceso de timbrado con PAC
├── ValidadorCFDI.py          # Validación de estructura CFDI
├── Correo.py                 # Envío de correos electrónicos
├── PDF.py                    # Generación de representación impresa
├── PreferenciasCliente.py    # Gestión de preferencias de usuario
├── ResultadoTimbrado.py      # Procesamiento de resultados
└── Configuration/
    ├── ConfiguracionLogin.py        # Lógica de autenticación
    ├── ConfiguracionRegistro.py     # Lógica de registro
    ├── ConfiguracionCertificados.py # Gestión de certificados
    └── ConfiguracionSello.py        # Configuración de sellado
```

**Características**:
- ✅ Independiente de la presentación
- ✅ Reutilizable por ambas APIs
- ✅ Contiene validaciones de negocio
- ✅ Orquesta operaciones complejas
- ✅ Maneja transacciones
- ✅ Integración con servicios externos (PAC, correo, etc.)
---

### Capa 3: DATA LAYER (Capa de Acceso a Datos)
**Responsabilidad**: Transformar y estructurar datos entre formatos

**Componentes principales**:
```
Data/
├── cartaPorte.py         # Manejo específico de Carta Porte
├── ConvertirJson.py      # Conversión JSON → XML CFDI
└── InterpreteJson.py     # Interpretación y validación de JSON
```

**Características**:
- ✅ Transformación de datos
- ✅ Validación de esquemas
- ✅ Mapeo de objetos
- ✅ Generación de XML SAT

---

### Capa 4: DATABASE LAYER (Capa de Base de Datos)
**Responsabilidad**: Persistencia y recuperación de datos

**Componentes principales**:
```
DB/
├── DBManager.py          # Gestor de conexiones y operaciones
├── settings.py           # Configuración de base de datos
```

**Características**:
- ✅ CRUD operations
- ✅ Connection pooling
- ✅ Gestión de transacciones

## Stack Tecnológico

### Backend
| Tecnología | Uso | Versión |
|-----------|-----|---------|
| **Python** | Lenguaje principal | 3.13+ |
| **FastAPI** | Framework web REST | 0.104.0+ |
| **Uvicorn** | Servidor ASGI | 0.24.0+ |
| **Pydantic** | Validación de datos y schemas | 2.0.0+ |
| **PostgreSQL** | Base de datos relacional | 12+ |
| **psycopg2-binary** | Driver PostgreSQL | 2.9.7 |
| **bcrypt** | Hash de contraseñas | 4.0.0+ |
| **python-dotenv** | Variables de entorno | 1.0.0+ |
| **satcfdi** | Librería CFDI SAT (Multi-PAC) | 4.8.1+ |
| **lxml** | Procesamiento y manipulación XML | Latest |
| **pdfkit** | Generación de PDFs desde HTML | 1.0.0+ |

### Frontend Clásico
| Tecnología | Uso |
|-----------|-----|
| **HTML5/CSS3** | Estructura y estilos |
| **JavaScript (Vanilla)** | Lógica del cliente |
| **Fetch API** | Comunicación con backend |

### Frontend React
| Tecnología | Uso | Versión |
|-----------|-----|---------|
| **React** | Framework UI | 18.x |
| **TypeScript** | Tipado estático | 5.x |
| **Vite** | Build tool | 5.x |
| **Tailwind CSS** | Framework CSS | 3.x |
| **React Router** | Enrutamiento | 6.x |

### DevOps y Scripts
| Herramienta | Uso |
|------------|-----|
| **PowerShell** | Scripts de automatización |
| **Git** | Control de versiones |
| **Cloudflare Tunnel** | Exposición pública (opcional) |

---

---

## Glosario de Términos

| Término | Definición |
|---------|------------|
| **Capa (Layer)** | Agrupación lógica de componentes con responsabilidades similares |
| **CFDI** | Comprobante Fiscal Digital por Internet (factura electrónica mexicana) |
| **PAC** | Proveedor Autorizado de Certificación del SAT |
| **CSD** | Certificado de Sello Digital (e.firma empresarial) |
| **Sellado** | Firma digital del XML con el CSD del emisor |
| **Timbrado** | Certificación del CFDI por el PAC y el SAT |
| **UUID** | Identificador único del comprobante fiscal |
| **Soft Delete** | Eliminación lógica (marcar como inactivo) en vez de física |
| **ORM** | Object-Relational Mapping (SQLAlchemy en este proyecto) |
| **API REST** | Interfaz de programación basada en HTTP |
| **Swagger** | Herramienta de documentación automática de APIs |

---
