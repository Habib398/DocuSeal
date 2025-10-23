# Sistema de Clave Única por Certificado

## Resumen
Cada certificado en el sistema ahora tiene una **clave única** (`claveUsuario`) generada automáticamente usando UUID v4.

## Características

### Generación Automática
- Se genera un UUID v4 al **crear** un nuevo certificado
- Utiliza `crypto.randomUUID()` del navegador (criptográficamente seguro)
- **Para certificados existentes sin clave**: Se genera automáticamente cuando se abre el modal de edición
- No se genera al editar un certificado que ya tiene clave (mantiene la misma)

### Visibilidad
- ✅ **SÍ se muestra** en los detalles del certificado (modal de edición)
- ❌ **NO se muestra** en la tabla de certificados
- Incluye botón para copiar al portapapeles

### Uso
- Esta clave se envía en los requests al servicio backend
- Se incluye en el JSON como `"claveUsuario": "uuid-generado"`
- Aparece al mismo nivel que `enviarCorreo` y `generarPDF`

## Ejemplo de JSON

```json
{
  "datosXML": { ... },
  "enviarCorreo": false,
  "generarPDF": false,
  "claveUsuario": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Implementación Frontend

### Archivos Modificados

1. **`apiClient.ts`**
   - Interfaz `Certificate` incluye campo `claveUsuario?: string`
   - Interfaz `CertificateFormData` incluye campo `claveUsuario?: string`

2. **`ModalCertificado.tsx`**
   - Genera UUID automáticamente al crear certificado
   - Muestra campo de solo lectura con botón copiar al editar
   - El campo solo es visible cuando se edita un certificado existente

3. **`TablaCertificados.tsx`**
   - NO muestra la columna `claveUsuario` (intencionalmente omitida)

## Backend (Pendiente)

### Tareas Necesarias

1. **Base de Datos**
   ```sql
   ALTER TABLE certificados ADD COLUMN claveUsuario VARCHAR(255) UNIQUE;
   ```

2. **Endpoint de Creación**
   - Recibir `claveUsuario` del frontend
   - Guardar en la BD asociada al certificado
   - Validar unicidad

3. **Endpoints de Servicio**
   - Usar `claveUsuario` en lugar de `noCertificado` para identificar certificados
   - Validar la clave en cada request
   - Ejemplo: `/api/v1/timbrar` con `"claveUsuario": "uuid"`

4. **Seguridad**
   - La clave NO debe ser encriptada (a diferencia de contraseñas)
   - Se usa como identificador único
   - Debe ser fácil de compartir con usuarios externos

## Flujo de Usuario

1. Usuario crea un nuevo certificado → Se genera UUID automáticamente
2. Usuario guarda el certificado → Backend recibe y almacena la clave
3. Usuario puede ver la clave al editar el certificado → La copia para usarla
4. Usuario usa la clave en requests al servicio backend
5. Backend valida la clave y devuelve datos del certificado correspondiente

### Certificados Existentes

Para certificados creados **antes** de esta implementación:

1. Usuario abre el certificado para editarlo
2. **Automáticamente** se genera una clave única si no existe
3. La clave se muestra en el campo correspondiente
4. Al guardar, la clave se envía al backend para almacenarse
5. Certificados futuros mantendrán su clave asignada

## Ventajas

✅ Identificación única y segura por certificado  
✅ No expone información sensible en la tabla  
✅ Fácil de copiar y compartir cuando se necesita  
✅ Compatible con el formato JSON de los endpoints  
✅ Reemplaza el uso de `noCertificado` (que puede no ser único)

## Notas

- La clave se genera en el **frontend** para mantener control del valor generado
- El backend debe validar que la clave sea única antes de guardar
- No se necesita recuperación de clave (siempre visible al editar el certificado)
