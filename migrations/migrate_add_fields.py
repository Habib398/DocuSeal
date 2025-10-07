"""
Script para agregar los campos correo y telefono a la tabla certificados_pac.
Ejecutar este script una vez para actualizar la base de datos existente.
"""
import psycopg2
from settings import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_new_fields():
    """Agrega los campos correo y telefono a la tabla certificados_pac si no existen."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='certificados_pac' 
            AND column_name IN ('correo', 'telefono')
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Agregar columna correo si no existe
        if 'correo' not in existing_columns:
            logger.info("Agregando columna 'correo' a certificados_pac...")
            cursor.execute("""
                ALTER TABLE certificados_pac 
                ADD COLUMN correo VARCHAR(255)
            """)
            logger.info("Columna 'correo' agregada exitosamente")
        else:
            logger.info("La columna 'correo' ya existe")
        
        # Agregar columna telefono si no existe
        if 'telefono' not in existing_columns:
            logger.info("Agregando columna 'telefono' a certificados_pac...")
            cursor.execute("""
                ALTER TABLE certificados_pac 
                ADD COLUMN telefono VARCHAR(50)
            """)
            logger.info("Columna 'telefono' agregada exitosamente")
        else:
            logger.info("La columna 'telefono' ya existe")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Migración completada exitosamente")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Error durante la migración: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Migración: Agregar campos correo y telefono")
    print("=" * 60)
    
    success = add_new_fields()
    
    if success:
        print("\n✓ Migración completada exitosamente")
        print("  - Campo 'correo' agregado/verificado")
        print("  - Campo 'telefono' agregado/verificado")
    else:
        print("\n✗ Error durante la migración")
        print("  Por favor revise los logs para más detalles")
