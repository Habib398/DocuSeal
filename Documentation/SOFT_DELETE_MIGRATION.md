# Migración: Soft Delete para Certificados

## Descripción

Se implementó un sistema de **soft delete** (eliminación lógica) para los certificados PAC. En lugar de eliminar físicamente los registros de la base de datos, ahora se marcan como inactivos mediante un campo booleano `activo`.

## Cambios Realizados

### Base de Datos

1. **Nueva columna**: Se agregó el campo `activo` (BOOLEAN) a la tabla `certificados_pac`
   - Valor por defecto: `TRUE`
   - Los certificados existentes se marcan automáticamente como activos

### Backend

1. **DBManager.py**:
   - Modificado `_normalize_cert_keys()`: Incluye el campo `activo` en la normalización
   - Modificado `get_all_certificados()`: Solo retorna certificados activos (`WHERE activo = TRUE`)
   - Modificado `delete_certificado()`: Ahora realiza un UPDATE en lugar de DELETE
     ```python
     UPDATE certificados_pac 
     SET activo = FALSE, updated_at = CURRENT_TIMESTAMP
     WHERE id = %s AND activo = TRUE
     ```

2. **ConfiguracionCertificados.py**:
   - Actualizada la documentación del método `eliminar_certificado()`
   - El método ahora marca el certificado como inactivo

3. **api_admin/main.py**:
   - Actualizado endpoint `DELETE /api/v1/certificados/{cert_id}`
   - Documentación actualizada para reflejar que es una desactivación

### Frontend

1. **main.js**:
   - Actualizado mensaje de éxito: "Certificado desactivado correctamente"
   - Actualizado mensaje de error: "Error al desactivar certificado"
   - Los comentarios ahora reflejan "desactivar" en lugar de "eliminar"

2. **index.html**:
   - Modal de confirmación actualizado:
     - Título: "Confirmar desactivación"
     - Mensaje: Explica que el certificado quedará inactivo pero se conserva
     - Botón: "Desactivar" (color warning) en lugar de "Eliminar" (danger)
   - Botón de acción: "Desactivar seleccionado" con icono `fa-ban`

## Ejecución de la Migración

### Opción 1: Script SQL Directo

```sql
-- Conectarse a la base de datos y ejecutar:
ALTER TABLE certificados_pac ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;
UPDATE certificados_pac SET activo = TRUE WHERE activo IS NULL;
```

### Opción 2: Script Python (Recomendado)

```bash
# Desde el directorio raíz del proyecto
python migrations/migrate_add_activo_field.py
```

Para revertir la migración (eliminar el campo):
```bash
python migrations/migrate_add_activo_field.py --rollback
```

## Beneficios

1. **Preservación de datos**: Los certificados nunca se eliminan físicamente
2. **Auditoría**: Se mantiene el historial completo de certificados
3. **Recuperación**: Posibilidad de reactivar certificados en el futuro
4. **Integridad**: Se preservan las relaciones con otras tablas si existen
5. **Cumplimiento**: Mejor alineado con prácticas de retención de datos

## Consultas Útiles

```sql
-- Ver todos los certificados (activos e inactivos)
SELECT id, usuarioPAC, nombreEmpresa, activo, created_at, updated_at
FROM certificados_pac
ORDER BY updated_at DESC;

-- Contar certificados por estado
SELECT activo, COUNT(*) as total
FROM certificados_pac
GROUP BY activo;

-- Reactivar un certificado
UPDATE certificados_pac 
SET activo = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE id = <ID>;

-- Ver certificados desactivados recientemente
SELECT * FROM certificados_pac
WHERE activo = FALSE
ORDER BY updated_at DESC
LIMIT 10;
```

## Consideraciones Futuras

1. **Panel de Administración**: Agregar una vista para gestionar certificados inactivos
2. **Reactivación**: Implementar funcionalidad para reactivar certificados
3. **Filtros**: Agregar filtro en el frontend para ver certificados inactivos
4. **Reportes**: Incluir métricas de certificados activos vs inactivos
5. **Limpieza**: Política de eliminación física de certificados inactivos después de X tiempo

## Compatibilidad

- **Retrocompatibilidad**: ✅ Los certificados existentes funcionan sin cambios
- **API**: ✅ Los endpoints mantienen la misma estructura
- **Frontend**: ✅ No requiere cambios en el código del cliente
- **Migraciones**: ✅ Puede ejecutarse en bases de datos con o sin datos

## Notas

- Los certificados inactivos **NO** aparecen en `get_all_certificados()`
- Para consultar certificados inactivos, sería necesario crear un nuevo endpoint
- El campo `updated_at` se actualiza automáticamente al desactivar
