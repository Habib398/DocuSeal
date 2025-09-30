# Ejemplos de JSON para los Endpoints de DocuSeal

Este directorio contiene ejemplos de formato JSON para cada endpoint disponible en la API de DocuSeal.

## Endpoints Disponibles

### 1. `/timbrar/` - POST
**Archivo de ejemplo:** `endpoint_timbrar_ejemplo.json`

**Descripción:** Timbra un XML que ya tiene sello digital.

**Campos requeridos:**
- `xml` (string): XML del CFDI ya sellado
- `usuario_pac` (string): Usuario del PAC
- `contrasena_pac` (string): Contraseña del PAC
- `pruebas` (boolean, opcional): Si es true usa ambiente de pruebas, por defecto true

---

### 2. `/sellar/` - POST
**Archivo de ejemplo:** `endpoint_sellar_ejemplo.json`

**Descripción:** Genera el sello digital para un CFDI a partir de datos JSON. Requiere que los certificados (CER y KEY) estén previamente almacenados en la base de datos.

**Campos requeridos:**
- `datos_xml` (object): Estructura JSON del CFDI
- `certificado.pwdCER` (string): Contraseña del certificado

**Nota:** Los archivos CER y KEY se obtienen automáticamente de la base de datos usando el campo `NoCertificado` del JSON.

---

### 3. `/timbrarSellar/` - POST
**Archivos de ejemplo:** 
- `endpoint_timbrarSellar_ejemplo.json` (para datos JSON)
- `endpoint_timbrarSellar_xml_string_ejemplo.json` (para XML como string)

**Descripción:** Combina el sellado y timbrado en una sola operación. Puede recibir datos JSON o XML como string.

**Campos requeridos:**
- `datos_xml` (object/string): Estructura JSON del CFDI o XML como string
- `certificado` (object): Información del certificado
  - `CER` (string): Certificado en Base64
  - `KEY` (string): Llave privada en Base64  
  - `pwdCER` (string): Contraseña del certificado
- `PAC` (object): Credenciales del PAC
  - `usuario` (string): Usuario del PAC
  - `contrasena` (string): Contraseña del PAC
- `pruebas` (boolean, opcional): Si es true usa ambiente de pruebas, por defecto true

---

### 4. `/timbrarSellarCartaPorte/` - POST
**Archivo de ejemplo:** `factura_carta_porte_ejemplo.json`

**Descripción:** Proceso completo de sellado y timbrado específico para CFDIs con complemento de Carta Porte 3.0. Incluye validaciones especializadas para este tipo de complemento.

**Campos requeridos:**
- `datos_xml` (object): Estructura JSON del CFDI con complemento CartaPorte
- `certificado` (object): Información del certificado
  - `CER` (string): Certificado en Base64
  - `KEY` (string): Llave privada en Base64
  - `pwdCER` (string): Contraseña del certificado
- `PAC` (object): Credenciales del PAC
  - `usuario` (string): Usuario del PAC
  - `contrasena` (string): Contraseña del PAC
- `pruebas` (boolean, opcional): Si es true usa ambiente de pruebas, por defecto true

**Validaciones específicas de Carta Porte:**
- Verifica la presencia del complemento `cartaporte30:CartaPorte`
- Valida estructura básica del complemento
- Asegura que tenga un `IdCCP` válido
- Valida ubicaciones (origen y destino)
- Valida mercancías
- Aplica validaciones específicas del SAT para Carta Porte 3.0

---

## Notas Importantes

1. **Certificados de Prueba:** Los ejemplos incluyen certificados de prueba del SAT. Para producción, usar certificados reales.

2. **Ambiente de Pruebas:** El campo `pruebas: true` indica que se usará el ambiente de pruebas del PAC.

3. **Estructura XML:** Todos los ejemplos siguen la estructura del CFDI 4.0 del SAT.

4. **Carta Porte:** El endpoint específico para Carta Porte incluye validaciones adicionales según los lineamientos del SAT.

5. **Base de Datos vs Archivos:** 
   - El endpoint `/sellar/` obtiene CER y KEY de la base de datos
   - Los demás endpoints requieren que se proporcionen en el JSON

## Estructura de Respuesta

Todos los endpoints devuelven un JSON con la siguiente estructura base:

```json
{
  "codigo": 0,  // 0 = éxito, != 0 = error
  "mensaje": "string",
  "xml_timbrado": "string",  // Solo en operaciones de timbrado exitosas
  "uuid": "string",          // UUID del timbre fiscal
  // ... otros campos específicos del endpoint
}
```