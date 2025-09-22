import sqlite3

class DBManager:
    def __init__(self, db_file="certificados_pac.db"):
        self.db_file = db_file

    def insert_certificado(self, usuarioPAC, contrasenaPAC, CER, KEY, vigencia, noCertificado, Certificado):
        """Inserta un nuevo registro en la tabla certificados_pac."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO certificados_pac (usuarioPAC, contrasenaPAC, CER, KEY, vigencia, noCertificado, Certificado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (usuarioPAC, contrasenaPAC, CER, KEY, vigencia, noCertificado, Certificado))
        conn.commit()
        conn.close()

    def get_certificado_by_usuario(self, usuarioPAC):
        """Obtiene un registro por usuarioPAC."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM certificados_pac WHERE usuarioPAC = ?
        """, (usuarioPAC,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def get_certificado_by_noCertificado(self, noCertificado):
        """Obtiene un registro por noCertificado."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM certificados_pac WHERE noCertificado = ?
        """, (noCertificado,))
        result = cursor.fetchone()
        conn.close()
        return result

    def delete_certificado(self, id):
        """Elimina un registro por id."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM certificados_pac WHERE id = ?
        """, (id,))
        conn.commit()
        conn.close()