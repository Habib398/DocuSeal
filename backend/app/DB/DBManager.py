import psycopg2 # type: ignore
from psycopg2.extras import RealDictCursor # type: ignore
import logging

# Importación flexible para settings
try:
    from .settings import get_db_connection
except ImportError:
    from settings import get_db_connection

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _normalize_cert_keys(cert_dict):
    # Convierte los nombres de columnas de PostgreSQL a camelCase para el frontend. (Copilot)
    if not cert_dict:
        return None
    return {
        'id': cert_dict.get('id'),
        'usuarioPAC': cert_dict.get('usuariopac'),
        'contrasenaPAC': cert_dict.get('contrasenapac'),
        'nombreEmpresa': cert_dict.get('nombreempresa'),
        'CER': cert_dict.get('cer'),
        'KEY': cert_dict.get('key'),
        'vigencia': str(cert_dict.get('vigencia')) if cert_dict.get('vigencia') else None,
        'noCertificado': cert_dict.get('nocertificado'),
        'Certificado': cert_dict.get('certificado'),
        'created_at': str(cert_dict.get('created_at')) if cert_dict.get('created_at') else None,
        'updated_at': str(cert_dict.get('updated_at')) if cert_dict.get('updated_at') else None
    }

class DBManager:
    def __init__(self):
        pass

    def _get_connection(self):
        # Obtiene una conexión a la base de datos
        return get_db_connection()

    def insert_certificado(self, usuarioPAC, contrasenaPAC, nombreEmpresa, CER, KEY, vigencia, noCertificado, Certificado):
        """Inserta un nuevo registro en la tabla certificados_pac."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO certificados_pac (usuarioPAC, contrasenaPAC, nombreEmpresa, CER, KEY, vigencia, noCertificado, Certificado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (usuarioPAC, contrasenaPAC, nombreEmpresa, CER, KEY, vigencia, noCertificado, Certificado))
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Certificado insertado exitosamente con ID: {new_id}")
            return new_id
            
        except psycopg2.Error as e:
            logger.error(f"Error insertando certificado: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise

    def get_certificado_by_usuario(self, usuarioPAC):
        """Obtiene un registro por usuarioPAC."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM certificados_pac WHERE usuarioPAC = %s
            """, (usuarioPAC,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return _normalize_cert_keys(dict(result)) if result else None
            
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo certificado por usuario: {e}")
            if conn:
                conn.close()
            raise
    
    def get_certificado_by_noCertificado(self, noCertificado):
        """Obtiene un registro por noCertificado."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM certificados_pac WHERE noCertificado = %s
            """, (noCertificado,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return _normalize_cert_keys(dict(result)) if result else None
            
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo certificado por número: {e}")
            if conn:
                conn.close()
            raise

    def get_all_certificados(self):
        """Obtiene todos los certificados."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM certificados_pac ORDER BY created_at DESC")
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [_normalize_cert_keys(dict(row)) for row in results] if results else []
            
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo todos los certificados: {e}")
            if conn:
                conn.close()
            raise
    
    # Métodos para gestión de usuarios
    def insert_usuario(self, name, email, password_hash):
        """Inserta un nuevo usuario en la tabla usuarios."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (name, email, password, verificacion)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, email, password_hash, False))
            
            new_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Usuario insertado exitosamente con ID: {new_id}")
            return new_id
            
        except psycopg2.Error as e:
            logger.error(f"Error insertando usuario: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise
    
    def get_usuario_by_email(self, email):
        """Obtiene un usuario por email."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM usuarios WHERE email = %s
            """, (email,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return dict(result) if result else None
            
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo usuario por email: {e}")
            if conn:
                conn.close()
            raise
    
    def update_verificacion(self, email, verificacion=True):
        """Actualiza el estado de verificación de un usuario."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios SET verificacion = %s WHERE email = %s
            """, (verificacion, email))
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Verificación actualizada para usuario: {email}")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Error actualizando verificación: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise

    def update_certificado(self, id, **kwargs):
        """Actualiza un certificado por ID."""
        conn = None
        try:
            if not kwargs:
                return False
                
            # Construir la consulta dinámicamente
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(id)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE certificados_pac 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, values)
            
            affected_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Certificado actualizado. Filas afectadas: {affected_rows}")
            return affected_rows > 0
            
        except psycopg2.Error as e:
            logger.error(f"Error actualizando certificado: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise

    def delete_certificado(self, id):
        """Elimina un registro por id."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM certificados_pac WHERE id = %s
            """, (id,))
            
            affected_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Certificado eliminado. Filas afectadas: {affected_rows}")
            return affected_rows > 0
            
        except psycopg2.Error as e:
            logger.error(f"Error eliminando certificado: {e}")
            if conn:
                conn.rollback()
                conn.close()
            raise