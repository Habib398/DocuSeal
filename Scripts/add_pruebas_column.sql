-- Agregar columna 'pruebas' a la tabla certificados_pac
-- Esta columna indica si el certificado es para pruebas (TRUE) o producción (FALSE)
-- El valor por defecto es TRUE para mantener compatibilidad con certificados existentes

ALTER TABLE certificados_pac 
ADD COLUMN IF NOT EXISTS pruebas BOOLEAN DEFAULT TRUE;

-- Comentario en la columna para documentación
COMMENT ON COLUMN certificados_pac.pruebas IS 'Indica si el certificado se utiliza para ambiente de pruebas (TRUE) o producción (FALSE)';
