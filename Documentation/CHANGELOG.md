# Changelog - DocuSeal

Registro de cambios y actualizaciones del sistema DocuSeal.

---

## [1.5.0] - 2025-10-08

### 🎉 Características Nuevas

#### Sistema de Soft Delete
- Implementado sistema de eliminación lógica en todas las tablas
- Campo `activo` agregado a: usuarios, certificados, preferencias_cliente
- Protección contra pérdida permanente de datos
- Scripts de migración incluidos en carpeta `migrations/`

#### Frontend React
- Iniciado desarrollo de frontend moderno con React 18 + TypeScript
- Configuración con Vite para desarrollo rápido
- Tailwind CSS para estilos
- Estructura de componentes modular
- Ubicación: `Frontend/react-app/`

#### Reorganización de Scripts
- Todos los scripts de inicio movidos a carpeta `Scripts/`
- Nuevo script: `start_with_cloudflare.ps1` para túnel público
- Scripts actualizados con mejor manejo de rutas y virtualenv

### 🔒 Seguridad

#### Migración Fernet → bcrypt
- Migrado sistema de passwords de Fernet a bcrypt
- bcrypt proporciona hash específico para passwords
- Salt único automático para cada password
- Mayor resistencia a ataques de fuerza bruta
- Cumplimiento con estándares de seguridad modernos

### 📚 Documentación

#### README.md Actualizado
- Agregada sección de características recientes
- Actualizada estructura del proyecto con nuevas carpetas
- Mejorada información sobre scripts de inicio
- Agregada información sobre frontend React
- Actualizado roadmap con versión 1.5.0

#### ARCHITECTURE.md Actualizado
- Agregada sección de Stack Tecnológico completo
- Nueva sección "Novedades v1.5.0"
- Documentación de sistema de soft delete
- Explicación de migración de seguridad
- Actualizada estructura de archivos
- Información detallada de scripts de inicio

#### Nuevo CHANGELOG.md
- Registro de cambios estructurado
- Versionado semántico
- Documentación de breaking changes

### 🔧 Mejoras

#### Base de Datos
- Índices optimizados para consultas con campo `activo`
- Scripts de migración automáticos
- Respaldos antes de migraciones

#### Scripts PowerShell
- Mejor detección de virtualenv
- Mensajes más claros y coloridos
- Manejo correcto de rutas relativas
- Soporte para múltiples configuraciones

### 📝 Documentación Adicional

Nuevos documentos agregados:
- `SOFT_DELETE_MIGRATION.md` - Guía completa del sistema soft delete
- `MIGRATION_README.md` - Guía de migraciones de base de datos
- `CAMBIOS_SOFT_DELETE.md` - Cambios técnicos del soft delete
- `SISTEMA_SOFT_DELETE_COMPLETADO.md` - Estado de implementación

---

## [1.0.0] - 2025-10-02

### 🎉 Release Inicial

#### APIs Separadas
- Service API (Puerto 8001) - API pública para servicios
- Admin API (Puerto 8002) - API administrativa para gestión

#### Funcionalidades Core
- Sellado de CFDI con certificados CSD
- Timbrado con PAC (Proveedor Autorizado de Certificación)
- Proceso completo: sellar y timbrar en un solo endpoint
- Generación de PDF representación impresa
- Validación de CFDI según reglas SAT

#### Gestión Administrativa
- Sistema de login y registro de usuarios
- CRUD completo de certificados digitales
- Panel web administrativo (HTML/CSS/JS)
- Gestión de preferencias de cliente

#### Arquitectura
- Separación en capas: Business, Data, Infrastructure
- Business Layer compartido entre ambas APIs
- DBManager para operaciones de base de datos
- Soporte para PostgreSQL y SQLite

#### Seguridad (Inicial)
- Encriptación de contraseñas con Fernet
- CORS configurado por API
- Validación de entrada en todos los endpoints

#### Documentación
- README.md completo
- ARCHITECTURE.md con diagramas
- Documentación Swagger automática
- Ejemplos de uso en carpeta `ejemplos/`

#### Scripts de Inicio
- `start_service.ps1` - Inicia Service API
- `start_admin.ps1` - Inicia Admin API  
- `start_all.ps1` - Inicia ambas APIs

---

## Convenciones de Versionado

Este proyecto sigue [Versionado Semántico](https://semver.org/):

- **MAJOR** (X.0.0): Cambios incompatibles con versiones anteriores
- **MINOR** (x.X.0): Nueva funcionalidad compatible con versiones anteriores
- **PATCH** (x.x.X): Corrección de bugs compatible con versiones anteriores

---

## Tipos de Cambios

- 🎉 **Características Nuevas**: Nueva funcionalidad
- 🔒 **Seguridad**: Mejoras de seguridad
- 🐛 **Correcciones**: Fixes de bugs
- 🔧 **Mejoras**: Mejoras de funcionalidad existente
- 📚 **Documentación**: Cambios en documentación
- ⚠️ **Breaking Changes**: Cambios que rompen compatibilidad
- 🗑️ **Deprecado**: Funcionalidad marcada para eliminación futura

---

## Roadmap

### v1.6.0 (Próximo)
- [ ] JWT Authentication para Admin API
- [ ] Sistema de roles y permisos
- [ ] Completar migración frontend a React
- [ ] Dashboard con métricas en tiempo real
- [ ] Rate limiting en Service API

### v1.7.0
- [ ] Soporte Carta Porte 3.0
- [ ] API de cancelación de CFDI
- [ ] Sistema de reportes avanzados
- [ ] Webhooks para eventos
- [ ] Notificaciones por email

### v2.0.0
- [ ] Soporte múltiples PACs
- [ ] Arquitectura de microservicios
- [ ] SDK multi-lenguaje
- [ ] Sistema de auditoría completo
- [ ] API GraphQL

---

**Última actualización**: 8 de Octubre de 2025
