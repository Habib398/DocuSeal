"""
Script de migración para agregar el campo 'activo' a la tabla certificados_pac.
Este campo permite realizar soft deletes, manteniendo el historial de certificados.

Ejecutar desde el directorio raíz:
python migrations/migrate_add_activo_field.py
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Añadir el directorio backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
sys.path.insert(0, backend_path)

try:
    from DB.settings import get_db_connection
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    logger.error("Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
    sys.exit(1)


def run_migration():
    """Ejecuta la migración para agregar el campo 'activo'"""
    conn = None
    try:
        logger.info("Conectando a la base de datos...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='certificados_pac' AND column_name='activo'
        """)
        
        if cursor.fetchone():
            logger.info("La columna 'activo' ya existe en la tabla certificados_pac")
            cursor.close()
            conn.close()
            return
        
        logger.info("Agregando columna 'activo' a la tabla certificados_pac...")
        
        # Agregar la columna
        cursor.execute("""
            ALTER TABLE certificados_pac 
            ADD COLUMN activo BOOLEAN DEFAULT TRUE
        """)
        
        # Actualizar registros existentes
        cursor.execute("""
            UPDATE certificados_pac 
            SET activo = TRUE 
            WHERE activo IS NULL
        """)
        
        conn.commit()
        logger.info("✓ Migración completada exitosamente")
        logger.info("✓ Columna 'activo' agregada a certificados_pac")
        logger.info("✓ Todos los certificados existentes marcados como activos")
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM certificados_pac WHERE activo = TRUE")
        count = cursor.fetchone()[0]
        logger.info(f"✓ Total de certificados activos: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"✗ Error durante la migración: {e}")
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)


def rollback_migration():
    """Revierte la migración (elimina el campo 'activo')"""
    conn = None
    try:
        logger.info("Conectando a la base de datos...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("Eliminando columna 'activo' de la tabla certificados_pac...")
        
        cursor.execute("""
            ALTER TABLE certificados_pac 
            DROP COLUMN IF EXISTS activo
        """)
        
        conn.commit()
        logger.info("✓ Rollback completado exitosamente")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"✗ Error durante el rollback: {e}")
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migración: Agregar campo activo a certificados_pac')
    parser.add_argument('--rollback', action='store_true', help='Revertir la migración')
    
    args = parser.parse_args()
    
    if args.rollback:
        logger.warning("⚠ Ejecutando ROLLBACK de la migración...")
        confirm = input("¿Estás seguro? Esta acción eliminará la columna 'activo'. (yes/no): ")
        if confirm.lower() == 'yes':
            rollback_migration()
        else:
            logger.info("Rollback cancelado")
    else:
        run_migration()
