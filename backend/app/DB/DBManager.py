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

class DBManager:
    def __init__(self):
        """Inicializa el DBManager para PostgreSQL"""
        pass

    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return get_db_connection()

    def insert_certificado(self, usuarioPAC, contrasenaPAC, nombreEmpresa, CER, KEY, vigencia, noCertificado, Certificado):
        """Inserta un nuevo registro en la tabla certificados_pac."""
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
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM certificados_pac WHERE usuarioPAC = %s
            """, (usuarioPAC,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return dict(result) if result else None
            
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo certificado por usuario: {e}")
            if conn:
                conn.close()
            raise
    
    def get_certificado_by_noCertificado(self, noCertificado):
        """Obtiene un registro por noCertificado."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM certificados_pac WHERE noCertificado = %s
            """, (noCertificado,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return dict(result) if result else None
            
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo certificado por número: {e}")
            if conn:
                conn.close()
            raise

    def get_all_certificados(self):
        """Obtiene todos los certificados."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM certificados_pac ORDER BY created_at DESC")
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [dict(row) for row in results] if results else []
            
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo todos los certificados: {e}")
            if conn:
                conn.close()
            raise

    def update_certificado(self, id, **kwargs):
        """Actualiza un certificado por ID."""
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