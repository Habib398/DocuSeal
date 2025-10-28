# Estandarización de Formato de Errores en DocuSeal

### 1. **api_service/routers/procesarComprobante.py**
- **Códigos añadidos:**
  - `PROC001`: Tipo de comprobante inválido
  - `PROC002`: Tipo no implementado
  - `PROC003`: Error interno del procesador

### 2. **Business/ServicioSellado.py**
- **Códigos añadidos:**
  - `SELL001`: Falta claveUsuario
  - `SELL002`: Falta XML o datosXML
  - `SELL003`: Tipo de comprobante invalido o no implementado aún
  - `SELL004`: Error inesperado en procesamiento JSON

### 3. **Business/ServicioTimbrado.py**
- **Códigos añadidos:**
  - `TIMB001`: Falta campo XML
  - `TIMB002`: Falta campo claveUsuario
  - `TIMB003`: Certificado no encontrado
  - `TIMB004`: Credenciales PAC incompletas
  - `TIMB005`: NoCertificado faltante
  - `TIMB006`: Error al acceder a la BD
  - `TIMB007`: Error al procesar XML

### 4. **Business/SellarXML.py**
- **Códigos añadidos:**
  - `SXML001`: Falta claveUsuario
  - `SXML002`: Error al convertir JSON a XML
  - `SXML003`: Debe proporcionar XML o datosXML
  - `SXML004`: Certificado no encontrado
  - `SXML005`: CER o KEY no encontrados
  - `SXML006`: Campo Certificado no encontrado
  - `SXML007`: NoCertificado no encontrado
  - `SXML008`: Error al parsear XML
  - `SXML009`: Error general en sellado

### 5. **Business/ResultadoTimbrado.py**
- **Códigos añadidos:**
  - `PAC000`: Error genérico del PAC (cuando no hay código específico)
  - Los códigos específicos del PAC (CFDI40xxx, etc.) se mantienen según la matriz de errores

### 6. **Business/ServicioTimbrarSellar.py**
- **Códigos añadidos:**
  - `TS001`: Falta claveUsuario
  - `TS002`: Falta XML o datosXML
  - `TS003`: Certificado no encontrado
  - `TS004`: Credenciales PAC incompletas
  - `TS005`: Error al acceder a la BD

### 7. **api_admin/main.py**
Todos los endpoints administrativos ahora retornan errores estandarizados:

#### Registro de Usuarios:
- `REG001`: Usuario ya registrado
- `REG002`: Error de validación en registro
- `REG003`: Error del servidor en registro
- `REG004`: Error inesperado en registro

#### Autenticación:
- `AUTH001`: Credenciales inválidas
- `AUTH002`: Error del servidor en login
- `AUTH003`: Error inesperado en login

#### Gestión de Certificados:
- `CERT001` a `CERT023`: Diversos errores relacionados con certificados
  - Obtención de certificados
  - Creación de certificados
  - Actualización de certificados
  - Eliminación de certificados
  - Reactivación de certificados

### 8. **Business/cfdi/Comprobantes/Traslados.py**
- `TRA001` a `TRA008`: Errores y warnings de comprobantes tipo Traslado

### 9. **Business/cfdi/Comprobantes/Ingreso.py**
- `ING001` a `ING007`: Errores y warnings de comprobantes tipo Ingreso

### 10. **Business/ValidadorCFDI.py**
- `LOC001` a `LOC012`: Validaciones locales de CFDI

## Convención de Códigos

Los códigos de error siguen un patrón lógico:

| Prefijo | Significado | Ejemplo |
|---------|-------------|---------|
| `PROC` | Procesamiento de comprobantes | `PROC001` |
| `SELL` | Servicio de sellado | `SELL001` |
| `TIMB` | Servicio de timbrado | `TIMB001` |
| `SXML` | Sellado XML | `SXML001` |
| `TS` | Timbrar y Sellar | `TS001` |
| `PAC` | Errores del PAC | `PAC000` |
| `REG` | Registro de usuarios | `REG001` |
| `AUTH` | Autenticación | `AUTH001` |
| `CERT` | Certificados | `CERT001` |
| `TRA` | Comprobante Traslado | `TRA001` |
| `ING` | Comprobante Ingreso | `ING001` |
| `LOC` | Validaciones locales | `LOC001` |