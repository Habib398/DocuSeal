# DocuSeal - Arquitectura Visual

## Arquitectura de Capas (4 Capas)

DocuSeal implementa una **arquitectura en capas (N-Tier Architecture)** simplificada que separa las responsabilidades del sistema en **4 capas independientes y reutilizables**. Esta arquitectura promueve la modularidad, mantenibilidad y escalabilidad del sistema.

### Capas del Sistema

1. **Presentation Layer** - APIs de exposición (Service API + Admin API)
2. **Business Layer** - Lógica de negocio y servicios externos
3. **Data Layer** - Transformación y estructuración de datos
4. **Database Layer** - Persistencia de datos
5. **Conection Layer** - Conexión y comunicación con el pac
### Principios de la Arquitectura de Capas

1. **Separación de Responsabilidades**: Cada capa tiene una función específica y bien definida
2. **Bajo Acoplamiento**: Las capas son independientes entre sí
3. **Alta Cohesión**: Cada capa agrupa funcionalidades relacionadas
4. **Reutilización**: Las capas inferiores son compartidas por ambas APIs
5. **Flujo Unidireccional**: Las capas superiores dependen de las inferiores, nunca al revés

---

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
