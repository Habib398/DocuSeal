-- Agregar campo 'activo' a la tabla certificados_pac
-- Este campo permitirá marcar certificados como inactivos sin eliminarlos

-- Agregar columna activo (por defecto TRUE para certificados existentes)
ALTER TABLE certificados_pac 
ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT TRUE;

-- Actualizar todos los registros existentes para que estén activos
UPDATE certificados_pac SET activo = TRUE WHERE activo IS NULL;

-- Modificar la consulta típica para solo obtener certificados activos
-- (Esta es una nota de documentación, la lógica se implementa en el código)
