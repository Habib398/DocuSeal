"""
Migración para agregar campo claveUsuario a la tabla certificados_pac
Este campo almacenará una clave única UUID para cada certificado
"""
import psycopg2
import sys
import os

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

from DB.settings import get_db_connection

def run_migration():
    """Ejecuta la migración para agregar columna claveUsuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Iniciando migración: agregar columna claveUsuario...")
        
        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='certificados_pac' AND column_name='claveusuario';
        """)
        
        if cursor.fetchone():
            print("La columna claveUsuario ya existe. No se requiere migración.")
            cursor.close()
            conn.close()
            return
        
        # Agregar columna claveUsuario
        cursor.execute("""
            ALTER TABLE certificados_pac 
            ADD COLUMN claveUsuario VARCHAR(255) UNIQUE;
        """)
        
        print("✓ Columna claveUsuario agregada exitosamente")
        
        # Generar claves UUID para certificados existentes que no tienen una
        cursor.execute("""
            UPDATE certificados_pac 
            SET claveUsuario = gen_random_uuid()::text 
            WHERE claveUsuario IS NULL;
        """)
        
        rows_updated = cursor.rowcount
        print(f"✓ Generadas claves UUID para {rows_updated} certificados existentes")
        
        conn.commit()
        print("✓ Migración completada exitosamente")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"✗ Error ejecutando migración: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

def rollback_migration():
    """Revierte la migración eliminando la columna claveUsuario"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Iniciando rollback: eliminando columna claveUsuario...")
        
        cursor.execute("""
            ALTER TABLE certificados_pac 
            DROP COLUMN IF EXISTS claveUsuario;
        """)
        
        conn.commit()
        print("✓ Rollback completado exitosamente")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"✗ Error ejecutando rollback: {e}")
        if conn:
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migración de base de datos: agregar claveUsuario')
    parser.add_argument('--rollback', action='store_true', help='Revertir la migración')
    
    args = parser.parse_args()
    
    if args.rollback:
        confirm = input("¿Estás seguro de que deseas revertir la migración? (yes/no): ")
        if confirm.lower() == 'yes':
            rollback_migration()
        else:
            print("Rollback cancelado")
    else:
        run_migration()
