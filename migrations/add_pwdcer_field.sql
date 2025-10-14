-- Migration: Agregar campo pwdCER a la tabla certificados_pac
-- Fecha: 2025-10-14
-- Descripción: Agrega el campo pwdCER para almacenar la contraseña de los certificados CER/KEY

-- Agregar columna pwdCER (requerido, NOT NULL, valor por defecto vacío)
ALTER TABLE certificados_pac 
ADD COLUMN IF NOT EXISTS pwdCER TEXT NOT NULL DEFAULT '';

-- Agregar comentario a la columna
COMMENT ON COLUMN certificados_pac.pwdCER IS 'Contraseña para descifrar los archivos CER y KEY (requerido, puede ser string vacío si no tiene contraseña)';
