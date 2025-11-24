import psycopg2 # type: ignore
import os
from dotenv import load_dotenv
from pathlib import Path

# Buscar archivo .env en múltiples ubicaciones
# settings.py está en: backend/app/DB/settings.py (4 niveles desde raíz)
# Necesitamos 4 niveles arriba para llegar a la raíz del proyecto
env_paths = [
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'),  # Raíz del proyecto (4 niveles arriba)
    os.path.join(os.getcwd(), '.env'),  # Working directory
    os.path.join(os.getcwd(), '..', '.env'),  # Parent de working directory
    os.path.join(os.path.expanduser('~'), 'DocuSeal', '.env'),  # Home/DocuSeal
]

env_found = False
for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        env_found = True
        break

if not env_found:
    # Si no encuentra .env, intenta cargar desde variables de entorno del sistema
    load_dotenv()

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'docuseal_db'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': os.getenv('DB_SSL_MODE', 'prefer')
}

def get_db_connection():
    """Obtiene una conexión a la base de datos PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        raise

def init_database():
    """Inicializa la base de datos y crea las tablas necesarias"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla certificados_pac
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificados_pac (
            id SERIAL PRIMARY KEY,
            usuarioPAC VARCHAR(255) NOT NULL,
            contrasenaPAC VARCHAR(255) NOT NULL,
            nombreEmpresa VARCHAR(255),
            CER TEXT NOT NULL,
            KEY TEXT NOT NULL,
            vigencia VARCHAR(50) NOT NULL,
            noCertificado VARCHAR(50) NOT NULL,
            Certificado TEXT NOT NULL,
            correo VARCHAR(255),
            telefono VARCHAR(50),
            pwdCER TEXT NOT NULL DEFAULT '',
            activo BOOLEAN DEFAULT TRUE,
            claveUsuario VARCHAR(255) UNIQUE,
            pruebas BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Crear tabla usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            verificacion BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Asegurar que la función gen_random_uuid() esté disponible (pgcrypto)
        cursor.execute("""
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
        """)
        
        # Generar claves UUID para certificados existentes que no tienen una
        cursor.execute("""
        UPDATE certificados_pac 
        SET claveUsuario = gen_random_uuid()::text 
        WHERE claveUsuario IS NULL;
        """)
        
        # Confirmar cambios
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Base de datos PostgreSQL y tablas creadas correctamente.")
        print("[OK] Tabla 'certificados_pac' creada/actualizada")
        print("[OK] Tabla 'usuarios' creada/actualizada")
        
    except psycopg2.Error as e:
        print(f"Error inicializando la base de datos: {e}")
        raise

if __name__ == "__main__":
    init_database()
