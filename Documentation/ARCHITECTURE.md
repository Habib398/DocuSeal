# DocuSeal - Arquitectura Visual

## 📐 Arquitectura de Capas (4 Capas)

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

## 🏗️ Diagrama Completo de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DOCUSEAL SYSTEM                                │
│                    Arquitectura en Capas (N-Tier)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┴────────────────────┐
                │                                        │
    ┌───────────▼──────────┐                ┌───────────▼──────────┐
    │                      │                │                      │
    │   SERVICE API        │                │   ADMIN API          │
    │   Puerto: 8001       │                │   Puerto: 8002       │
    │                      │                │                      │
    │   🌐 PÚBLICO         │                │   🔒 INTERNO         │
    │                      │                │                      │
    │   - /timbrar         │                │   - /api/login       │
    │   - /sellar          │                │   - /api/register    │
    │   - /timbrarSellar   │                │   - /api/v1/cert*    │
    │   - /health          │                │   - /api/v1/prefs*   │
    │                      │                │                      │
    └──────────┬───────────┘                └───────────┬──────────┘
               │                                        │
               │         CAPA DE PRESENTACIÓN           │
               │         (Presentation Layer)           │
               │                                        │
               └────────────────┬───────────────────────┘
                                │
                  ┌─────────────▼─────────────────────┐
                  │                                   │
                  │   BUSINESS LAYER                  │
                  │   Lógica de Negocio               │
                  │   (Compartida)                    │
                  │                                   │
                  │   - SellarXML.py                  │
                  │   - Timbrado.py                   │
                  │   - ValidadorCFDI.py              │
                  │   - Correo.py                     │
                  │   - PDF.py                        │
                  │   - Configuraciones               │
                  │   - Comunicación con PAC          │
                  │                                   │
                  └─────────────┬─────────────────────┘
                                │
                  ┌─────────────▼─────────────────────┐
                  │                                   │
                  │   DATA LAYER                      │
                  │   Acceso y Transformación         │
                  │   (Compartida)                    │
                  │                                   │
                  │   - cartaPorte.py                 │
                  │   - ConvertirJson.py              │
                  │   - InterpreteJson.py             │
                  │                                   │
                  └─────────────┬─────────────────────┘
                                │
                  ┌─────────────▼─────────────────────┐
                  │                                   │
                  │   DATABASE LAYER                  │
                  │   Persistencia                    │
                  │   (Compartida)                    │
                  │                                   │
                  │   - DBManager.py                  │
                  │   - settings.py                   │
                  │   - PostgreSQL                    │
                  │                                   │
                  └───────────────────────────────────┘
```

---

## 🎯 Separación de APIs (Capa de Presentación)

Las dos APIs actúan como la **Capa de Presentación** del sistema, cada una con responsabilidades distintas:

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
        ┌───────▼────────┐          ┌───────▼────────┐
        │  SERVICE API   │          │   ADMIN API    │
        │  Puerto: 8001  │          │  Puerto: 8002  │
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
                    │   DATABASE LAYER   │
                    │   (Compartido)     │
                    └────────────────────┘
```

## � Descripción Detallada de Capas

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

**Ubicación**: `backend/app/Business/`

**Nota**: Esta capa ahora también maneja la comunicación con servicios externos como el PAC del SAT, integrando lo que antes era la capa de infraestructura.

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

**Ubicación**: `backend/app/Data/`

---

### Capa 4: DATABASE LAYER (Capa de Base de Datos)
**Responsabilidad**: Persistencia y recuperación de datos

**Componentes principales**:
```
DB/
├── DBManager.py          # Gestor de conexiones y operaciones
├── settings.py           # Configuración de base de datos
└── migrations/           # Scripts de migración
```

**Características**:
- ✅ CRUD operations
- ✅ Connection pooling
- ✅ Gestión de transacciones
- ✅ Sistema de soft delete
- ✅ Migraciones de esquema

**Ubicación**: `backend/app/DB/`


## 🔧 Stack Tecnológico

### Backend
| Tecnología | Uso | Versión |
|-----------|-----|---------|
| **Python** | Lenguaje principal | 3.10+ |
| **FastAPI** | Framework web | Latest |
| **Uvicorn** | Servidor ASGI | Latest |
| **SQLAlchemy** | ORM | Latest |
| **PostgreSQL** | Base de datos | 12+ |
| **bcrypt** | Hash de passwords | Latest |
| **Cryptography** | Manejo de certificados | Latest |
| **ReportLab** | Generación de PDFs | Latest |
| **lxml** | Procesamiento XML | Latest |

### Frontend Clásico
| Tecnología | Uso |
|-----------|-----|
| **HTML5/CSS3** | Estructura y estilos |
| **JavaScript (Vanilla)** | Lógica del cliente |
| **Fetch API** | Comunicación con backend |

### Frontend React (En desarrollo)
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

## 📚 Glosario de Términos

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


**Última actualización**: 10 de Octubre de 2025  
**Versión del Sistema**: 1.5.0  
**Versión del Documento**: 2.1
