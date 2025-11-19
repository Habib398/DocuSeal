# Implementación de Soporte Multi-PAC

## 🎯 Resumen Ejecutivo

**Estado**: ✅ Infraestructura base lista | ⏳ Activación pendiente

Este documento detalla la implementación del soporte multi-PAC en DocuSeal. El código está implementado y comentado, listo para activar.

**Archivos listos:**
- ✅ Backend: Endpoint y validación (comentados en `api_admin/main.py`)
- ✅ Frontend: Componente SelectPAC (comentado en `components/SelectPAC.tsx`)
- ✅ Arquitectura: Clases base y factory pattern implementados

---

## PACs Disponibles en satcfdi

La librería `satcfdi` versión 4.8.1 incluye soporte para:
- comerciodigital (actual)
- diverza
- finkok
- mysuite
- prodigia
- sat
- swsapien

## Cambios Necesarios

### 1. Base de Datos
Agregar campo `tipoPAC` a la tabla `certificados_pac`:

```sql
ALTER TABLE certificados_pac 
ADD COLUMN tipoPAC VARCHAR(50) DEFAULT 'comerciodigital' NOT NULL;
```

### 2. DBManager
Actualizar `backend/app/DB/DBManager.py`:

- Método `_normalize_cert_keys`: agregar `'tipoPAC': cert_dict.get('tipopac')`
- Método `insert_certificado`: agregar parámetro `tipoPAC='comerciodigital'`
- Actualizar todas las consultas SQL que insertan certificados

### 3. Factory Pattern para PACs
Archivo base creado en `backend/app/Business/PACFactory.py`

El archivo contiene:
- Estructura base de la clase `PACFactory` con documentación completa
- Métodos preparados para implementación futura:
  - `crear_pac()` - Actualmente lanza `NotImplementedError`
  - `tipos_disponibles()` - Retorna lista vacía
  - `es_pac_valido()` - Valida tipos de PAC
  - `obtener_pac_default()` - Retorna 'comerciodigital'
- Funciones utilitarias de soporte

**Implementación futura:**
Se descomentarán las importaciones de `satcfdi.pacs` y se completará la lógica cuando esté lista la migración multi-PAC.

### 4. Modificar Timbrado.py
**Archivo**: `backend/app/Business/Timbrado.py`
**Cambios necesarios cuando se active:**
1. Importar PACFactory y modificar creación de PAC (línea ~28):
```python
# Actualmente:
pac = ComercioDigital(user=usuario_pac, password=contrasena_pac, environment=env)

# Cambiar a:
from .PACFactory import PACFactory
pac = PACFactory.crear_pac(tipo_pac, usuario_pac, contrasena_pac, pruebas)
```
2. Agregar parámetro `tipo_pac` a los métodos:
   - `timbrar_cfdi(cls, xml, usuario_pac, contrasena_pac, pruebas, tipo_pac='comerciodigital')`
   - `_procesar_timbrado(cls, xml, usuario_pac, contrasena_pac, pruebas, tipo_pac='comerciodigital')`

### 5. Modificar Cancelacion.py
**Nota Importante:** La librería `satcfdi` **no incluye soporte para cancelación con Comercio Digital**. 
El método actual en `Cancelacion.py` usa una implementación personalizada. Otros PACs como Finkok, Diverza, MySuite, Prodigia y SWSapien sí tienen soporte nativo en `satcfdi` para cancelación.

**Plan de implementación futura:**
- Detectar el tipo de PAC del certificado
- Si es `comerciodigital`: Usar la implementación personalizada actual
- Si es otro PAC: Usar el método de cancelación nativo de `satcfdi`
- Agregar parámetro `tipo_pac` al método `cancelar_uuid` para enrutamiento adecuado

**Referencia de cambio (cuando se implemente):**
```python
# Reemplazar línea 124:
# Antes:
pac = ComercioDigital(
    user=usuario_pac,
    password=password_pac,
    environment=environment
)

# Después:
# Enrutamiento basado en tipo_pac:
if tipo_pac == 'comerciodigital':
    # Usar implementación personalizada
    resultado = ComercioDigital.cancelar_uuid(...)
else:
    # Usar implementación de satcfdi
    from .PACFactory import PACFactory
    pac = PACFactory.crear_pac(tipo_pac, usuario_pac, password_pac, pruebas)
    resultado = pac.cancel(...)
```

**Archivos disponibles:**

1. ✅ **`backend/app/Business/Cancelacion/CancelacionPAC.py`**
   - Clase abstracta `CancelacionPAC` con interfaz común
   - Métodos: `cancelar()`, `validar_parametros()`, `obtener_tipo_pac()`, `formatear_respuesta()`
   - Clase `CancelacionPACException` para manejo de errores

2. ✅ **`backend/app/Business/Cancelacion/CancelacionComercioDigital.py`**
   - Implementación completa para Comercio Digital
   - Migrada desde `Cancelacion.py` original
   - Hereda de `CancelacionPAC`

3. ✅ **`backend/app/Business/Cancelacion/CancelacionGenericaPAC.py`**
   - Implementación preparada para otros PACs (Finkok, Diverza, MySuite, Prodigia, SWSapien)
   - Usa soporte nativo de `satcfdi` (pendiente activación)
   - Hereda de `CancelacionPAC`

4. ✅ **`backend/app/Business/Cancelacion.py` (modificado)**
   - Actúa como wrapper de compatibilidad
   - Delega a `CancelacionComercioDigital`


### 6. Servicios (Service Layer)
Actualizar `backend/app/Business/Services/ServicioTimbrado.py`:

```python
# Obtener tipo de PAC desde el certificado
tipo_pac = certificado.get('tipoPAC', 'comerciodigital')

# Pasar tipo_pac al servicio de timbrado
resultado_timbrado = TimbradoService.timbrar_cfdi(
    xml_input, 
    usuario_pac, 
    contrasena_pac, 
    pruebas,
    tipo_pac=tipo_pac
)
```

Aplicar cambio similar en `ServicioCancelacion.py`.

### 7. API Admin
✅ **PREPARADO** - Código comentado y listo para activar

**Archivos modificados:**
- `backend/app/api_admin/main.py`

**Cambios implementados (comentados):**

1. ✅ **Nuevo endpoint `/v1/pacs/tipos`**
   - Retorna lista de PACs disponibles con información detallada
   - Incluye flags de funcionalidades (timbrado, cancelación)
   - Identifica PAC por defecto

2. ✅ **Validación de tipoPAC en `/v1/certificados/`**
   - Valida que el tipo de PAC sea soportado
   - Usa `PACFactory.es_pac_valido()`
   - Retorna error descriptivo si el PAC no es válido

**Para activar:**
- Descomentar el bloque de código marcado con `# ENDPOINT MULTI-PAC`
- Descomentar la validación en el endpoint de crear certificado

### 8. Frontend
✅ **PREPARADO** - Componentes listos para integrar

**Archivos creados:**

1. ✅ **`SelectPAC.tsx`** - Componente selector de PAC
   - Obtiene lista de PACs desde el backend
   - Muestra información y capacidades de cada PAC
   - Maneja estados de carga y error
   - Fallback a Comercio Digital si falla
   - **Estado:** Completamente comentado, listo para activar

2. ✅ **`INTEGRATION_INSTRUCTIONS_MULTI_PAC.tsx`** - Guía de integración
   - Instrucciones paso a paso (10 pasos)
   - Referencias exactas de código
   - Ubicación visual del componente
   - Checklist de testing

**Para activar:**
1. Descomentar código en `SelectPAC.tsx`
2. Importar en `ModalCertificado.tsx`
3. Agregar campo `tipoPAC` al formulario
4. Agregar `tipoPAC` a la interfaz `CertificateFormData`
5. Seguir instrucciones en `INTEGRATION_INSTRUCTIONS_MULTI_PAC.tsx`

**Características del selector:**
- Lista desplegable con PACs activos
- Muestra descripción y capacidades
- Indica si requiere configuración especial
- Valor por defecto: 'comerciodigital'
- Validación en frontend y backend

---
### Pendiente (Cuando se active)

| Componente | Descripción |
|------------|-------------|
| Migración BD | Agregar campo `tipoPAC` a tabla `certificados_pac` |
| DBManager | Actualizar métodos para soportar `tipoPAC` |
| PACFactory | Descomentar importaciones y completar `crear_pac()` |
| Timbrado.py | Agregar soporte para múltiples PACs |
| Services | Pasar `tipo_pac` desde certificado a servicios |
| Frontend Integration | Descomentar y conectar SelectPAC |

---

## 🚀 Guía de Activación Rápida

### Opción 1: Solo Frontend (Sin BD)

#### Backend
**Archivo**: `backend/app/api_admin/main.py`

1. Buscar: `# ENDPOINT MULTI-PAC (PREPARADO PARA FUTURO)`
2. Descomentar el bloque entre `"""` (endpoint `/v1/pacs/tipos`)
3. Buscar: `# VALIDACIÓN MULTI-PAC (PREPARADA PARA FUTURO)`
4. Descomentar el bloque entre `"""`

#### Frontend
**Archivo**: `Frontend/react-app/src/components/SelectPAC.tsx`

1. Descomentar todo el código entre `/*` y `*/` (líneas ~14-150)
2. Eliminar la línea `export default null;`

**Archivo**: `Frontend/react-app/src/components/ModalCertificado.tsx`

1. Agregar import:
```tsx
import SelectPAC from './SelectPAC';
```

2. Modificar `emptyFormData` (~línea 65):
```tsx
const emptyFormData: CertificateFormData = {
  // ... campos existentes ...
  tipoPAC: 'comerciodigital', // ← AGREGAR
};
```

3. Agregar handler (después de `handleChange`):
```tsx
const handlePACChange = (newPAC: string) => {
  setFormData({ ...formData, tipoPAC: newPAC });
};
```

4. Agregar componente en JSX (después del checkbox "Ambiente de Pruebas"):
```tsx
<div className="col-md-6">
  <SelectPAC
    value={formData.tipoPAC || 'comerciodigital'}
    onChange={handlePACChange}
    disabled={loading}
  />
</div>
```

**Archivo**: `Frontend/react-app/src/services/apiClient.ts`

```tsx
export interface CertificateFormData {
  // ... campos existentes ...
  tipoPAC?: string; // ← AGREGAR
}
```

#### Testing
1. Reiniciar backend y frontend
2. Abrir modal de certificados
3. Verificar que aparezca selector de PAC
4. Crear certificado de prueba

### Opción 2: Completo (Con BD)

Seguir **Opción 1** y además:

#### Base de Datos
```sql
ALTER TABLE certificados_pac 
ADD COLUMN tipoPAC VARCHAR(50) DEFAULT 'comerciodigital' NOT NULL;
```

#### DBManager
**Archivo**: `backend/app/DB/DBManager.py`

1. En `_normalize_cert_keys`:
```python
'tipoPAC': cert_dict.get('tipopac', 'comerciodigital')
```

2. En `insert_certificado`, agregar parámetro:
```python
def insert_certificado(self, ..., tipoPAC: str = 'comerciodigital'):
```

3. Actualizar SQL INSERT para incluir `tipoPAC`

---

## Notas Importantes

- Cada PAC puede tener diferentes tiempos de respuesta
- Los códigos de error varían entre PACs
- Las credenciales de prueba deben obtenerse de cada proveedor
- Algunos PACs pueden requerir configuración adicional (IPs autorizadas, certificados, etc.)
- Verificar límites de timbrado por PAC (algunos tienen restricciones diferentes)
- **La implementación actual NO afecta el funcionamiento del sistema**
- **Todo el código nuevo está comentado o aislado**
- **Retrocompatible al 100% con certificados existentes**
```
