"""
Módulo de configuración y lógica para el login de usuarios.
"""
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr

try:
    import bcrypt
except ImportError:
    bcrypt = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UsuarioLoginRequest(BaseModel):
    """Modelo para la solicitud de login de usuario."""
    email: EmailStr
    password: str


class ConfiguracionLogin:
    """Clase para manejar la lógica de autenticación de usuarios."""
    
    def __init__(self, db_manager):
        """
        Inicializa el servicio de login.
        
        Args:
            db_manager: Instancia de DBManager para operaciones de BD
        """
        self.db_manager = db_manager
    
    def verificar_password(self, password_plano: str, password_hash: str) -> bool:
        """
        Verifica que la contraseña coincida con el hash almacenado.
        
        Args:
            password_plano: Contraseña en texto plano
            password_hash: Hash de la contraseña almacenado en BD
            
        Returns:
            True si coinciden, False en caso contrario
            
        Raises:
            RuntimeError: Si bcrypt no está disponible
        """
        if bcrypt is None:
            raise RuntimeError("bcrypt no está instalado. Instale con: pip install bcrypt")
        
        try:
            password_bytes = password_plano.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception as e:
            logger.error(f"Error al verificar contraseña: {e}")
            return False
    
    def obtener_usuario(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Diccionario con datos del usuario o None si no existe
        """
        try:
            usuario = self.db_manager.get_usuario_by_email(email)
            return usuario
        except Exception as e:
            logger.error(f"Error al obtener usuario: {e}")
            return None
    
    def autenticar_usuario(self, credenciales: UsuarioLoginRequest) -> Dict[str, Any]:
        """
        Autentica un usuario con sus credenciales.
        
        Args:
            credenciales: Credenciales del usuario (email y password)
            
        Returns:
            Diccionario con resultado de autenticación
            
        Raises:
            ValueError: Si las credenciales son inválidas
            RuntimeError: Si hay error en el proceso
        """
        try:
            # Buscar usuario por email
            usuario = self.obtener_usuario(credenciales.email)
            
            if not usuario:
                logger.warning(f"Intento de login con email inexistente: {credenciales.email}")
                raise ValueError("Credenciales inválidas")
            
            # Verificar contraseña
            password_valido = self.verificar_password(
                credenciales.password,
                usuario['password']
            )
            
            if not password_valido:
                logger.warning(f"Intento de login con contraseña incorrecta: {credenciales.email}")
                raise ValueError("Credenciales inválidas")
            
            # Login exitoso
            logger.info(f"Login exitoso: {credenciales.email}")
            
            # Preparar respuesta (sin incluir la contraseña)
            return {
                "success": True,
                "message": "Login exitoso",
                "user": {
                    "id": usuario['id'],
                    "name": usuario['name'],
                    "email": usuario['email'],
                    "verificacion": usuario.get('verificacion', False)
                }
            }
            
        except ValueError as e:
            # Errores de autenticación
            logger.warning(f"Error de autenticación: {e}")
            raise
        except Exception as e:
            # Errores inesperados
            logger.error(f"Error al autenticar usuario: {e}")
            raise RuntimeError(f"Error en el proceso de autenticación: {str(e)}")
    
    def validar_sesion_activa(self, user_id: int) -> bool:
        """
        Valida si un usuario tiene una sesión activa (implementación futura).
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si la sesión es válida
            
        Note:
            Esta función está preparada para futuras implementaciones
            con tokens JWT o sesiones en base de datos.
        """
        # TODO: Implementar validación de sesión con tokens
        # Por ahora siempre retorna True
        return True
    
    def registrar_ultimo_login(self, user_id: int) -> None:
        """
        Registra la fecha del último login (implementación futura).
        
        Args:
            user_id: ID del usuario
            
        Note:
            Esta función está preparada para futuras implementaciones
            que requieran registrar el último acceso del usuario.
        """
        # TODO: Implementar registro de último login en BD
        # Requeriría añadir campo last_login en la tabla usuarios
        pass
