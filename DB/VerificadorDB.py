import sqlite3

conn = sqlite3.connect("certificados_pac.db")
cursor = conn.cursor()

# Ver nombres de tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tablas:", cursor.fetchall())

# Ver columnas de la tabla certificados_pac
cursor.execute("PRAGMA table_info(certificados_pac);")
print("Columnas:", cursor.fetchall())

# Ver contenido de la tabla certificados_pac
cursor.execute("SELECT * FROM certificados_pac;")
print("Contenido:", cursor.fetchall())

conn.close()