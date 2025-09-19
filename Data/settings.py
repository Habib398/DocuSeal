import sqlite3

# Nombre del archivo de la base de datos
db_file = "certificados_pac.db"

# Conexión a la base de datos (si no existe, se crea)
conn = sqlite3.connect(db_file)

# Crear un cursor para ejecutar sentencias SQL
cursor = conn.cursor()

# Crear tabla (si no existe ya)
cursor.execute("""
CREATE TABLE IF NOT EXISTS certificados_pac (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarioPAC TEXT NOT NULL,
    contrasenaPAC TEXT NOT NULL,
    CER TEXT NOT NULL,
    KEY TEXT NOT NULL,
    vigencia TEXT NOT NULL,
    noCertificado TEXT NOT NULL,
    Certificado TEXT NOT NULL
);
""")

# Confirmar cambios
conn.commit()

# Cerrar conexión
conn.close()

print("Base de datos y tabla 'certificados_pac' creadas correctamente.")
