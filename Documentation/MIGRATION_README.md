# Actualización de la Base de Datos - Campos Correo y Teléfono

## Cambios Realizados

Se han agregado dos nuevos campos a la tabla `certificados_pac`:
- **correo**: Campo de tipo VARCHAR(255) para almacenar el correo electrónico de contacto
- **telefono**: Campo de tipo VARCHAR(50) para almacenar el número de teléfono de contacto

## Archivos Modificados

### Backend
1. **`backend/app/DB/settings.py`**
   - Actualizada la definición de la tabla para incluir los campos `correo` y `telefono`

2. **`backend/app/DB/DBManager.py`**
   - Actualizado `_normalize_cert_keys()` para incluir los nuevos campos
   - Actualizado `insert_certificado()` para aceptar los parámetros `correo` y `telefono`

3. **`backend/app/Business/Configuration/ConfiguracionCertificados.py`**
   - Actualizado `crear_certificado()` para pasar los campos `correo` y `telefono` al DBManager

### Frontend
1. **`Frontend/index.html`**
   - Agregados campos de entrada para correo y teléfono en el formulario modal
   - La tabla ya tenía las columnas definidas, ahora mostrarán datos correctamente

2. **`Frontend/js/main.js`**
   - Actualizado `renderCertificados()` para mostrar los nuevos campos en la tabla
   - Actualizado `editSelected()` para cargar los valores de correo y teléfono al editar
   - Actualizado `saveCertificado()` para incluir correo y teléfono al guardar
   - Actualizado `searchCertificados()` para mostrar correctamente todas las columnas
   - Actualizado colspan de 4 a 7 en mensajes vacíos

## Cómo Ejecutar la Migración

### Opción 1: Base de Datos Nueva
Si estás creando la base de datos desde cero, simplemente ejecuta:

```powershell
cd backend\app\DB
python settings.py
```

Esto creará las tablas con los nuevos campos ya incluidos.

### Opción 2: Base de Datos Existente
Si ya tienes datos en la base de datos, ejecuta el script de migración:

```powershell
cd backend\app\DB
python migrate_add_fields.py
```

Este script:
- ✓ Verifica si las columnas ya existen
- ✓ Agrega las columnas solo si no están presentes
- ✓ Es seguro ejecutarlo múltiples veces
- ✓ No afecta los datos existentes

## Verificación

Después de ejecutar la migración, puedes verificar que todo funciona correctamente:

1. **Inicia el servidor backend:**
   ```powershell
   .\start_admin.ps1
   ```

2. **Abre el frontend** en tu navegador:
   ```
   http://localhost:8000/static/index.html
   ```

3. **Prueba las funcionalidades:**
   - Crea un nuevo certificado con correo y teléfono
   - Edita un certificado existente y agrega correo/teléfono
   - Verifica que los datos se muestren correctamente en la tabla

## Estructura de la Tabla Actualizada

```sql
CREATE TABLE certificados_pac (
    id SERIAL PRIMARY KEY,
    usuarioPAC VARCHAR(255) NOT NULL,
    contrasenaPAC VARCHAR(255) NOT NULL,
    nombreEmpresa VARCHAR(255),
    CER TEXT NOT NULL,
    KEY TEXT NOT NULL,
    vigencia VARCHAR(50) NOT NULL,
    noCertificado VARCHAR(50) NOT NULL,
    Certificado TEXT NOT NULL,
    correo VARCHAR(255),           -- NUEVO
    telefono VARCHAR(50),           -- NUEVO
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Vista de la Tabla en el Frontend

La tabla ahora muestra 7 columnas:
1. ID
2. Usuario PAC
3. Empresa
4. No. Certificado
5. Vigencia
6. Correo
7. Teléfono

Los campos opcionales (correo, teléfono, empresa) mostrarán "-" cuando estén vacíos.

## Notas Importantes

- Los campos `correo` y `telefono` son **opcionales**
- El campo `correo` valida formato de email en el frontend
- Los datos existentes no se verán afectados
- Los certificados sin correo/teléfono mostrarán "-" en la tabla
