"""
Migration script para agregar el campo pwdCER a la tabla certificados_pac
Ejecutar: python migrations/migrate_add_pwdcer_field.py
"""

import psycopg2
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')))

from DB.settings import get_db_connection

def migrate():
    """Ejecuta la migración para agregar el campo pwdCER"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Iniciando migración: Agregar campo pwdCER...")
        
        # Leer el archivo SQL
        sql_file = os.path.join(os.path.dirname(__file__), 'add_pwdcer_field.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Ejecutar la migración
        cursor.execute(sql_content)
        conn.commit()
        
        print("✓ Campo pwdCER agregado exitosamente")
        print("✓ Migración completada")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"✗ Error durante la migración: {e}")
        if conn:
            conn.rollback()
            conn.close()
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error general: {e}")
        if conn:
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    migrate()
