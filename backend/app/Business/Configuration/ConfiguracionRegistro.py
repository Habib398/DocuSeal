"""
Módulo de configuración y lógica para el registro de usuarios.
"""
import logging
from typing import Dict, Any
from pydantic import BaseModel, EmailStr

try:
    import bcrypt
except ImportError:
    bcrypt = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UsuarioRegistroRequest(BaseModel):
    """Modelo para la solicitud de registro de usuario."""
    name: str
    email: EmailStr
    password: str
    confirm_password: str


class ConfiguracionRegistro:
    """Clase para manejar la lógica de registro de usuarios."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def validar_passwords(self, password: str, confirm_password: str) -> tuple[bool, str]:
        if password != confirm_password:
            return False, "Las contraseñas no coinciden"
        
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        return True, ""
    
    def validar_fortaleza_password(self, password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        return True, ""
    
    def hashear_password(self, password: str) -> str:
        if bcrypt is None:
            raise RuntimeError("bcrypt no está instalado. Instale con: pip install bcrypt")
        
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        return password_hash.decode('utf-8')
    
    def verificar_email_disponible(self, email: str) -> tuple[bool, str]:
        try:
            usuario_existente = self.db_manager.get_usuario_by_email(email)
            if usuario_existente:
                return False, "El email ya está registrado"
            return True, ""
        except Exception as e:
            logger.error(f"Error verificando email: {e}")
            return False, f"Error al verificar email: {str(e)}"
    
    def registrar_usuario(self, datos: UsuarioRegistroRequest) -> Dict[str, Any]:

        try:
            # Validar contraseñas
            valido, mensaje = self.validar_passwords(datos.password, datos.confirm_password)
            if not valido:
                raise ValueError(mensaje)
            
            # Verificar email disponible
            disponible, mensaje = self.verificar_email_disponible(datos.email)
            if not disponible:
                raise ValueError(mensaje)
            
            # Hashear contraseña
            password_hash = self.hashear_password(datos.password)
            
            # Insertar usuario en BD
            user_id = self.db_manager.insert_usuario(
                name=datos.name,
                email=datos.email,
                password_hash=password_hash
            )
            
            logger.info(f"Usuario registrado exitosamente: {datos.email} (ID: {user_id})")
            
            return {
                "success": True,
                "message": "Usuario registrado exitosamente",
                "id": user_id,
                "email": datos.email
            }
            
        except ValueError as e:
            # Errores de validación
            logger.warning(f"Error de validación en registro: {e}")
            raise
        except Exception as e:
            # Errores inesperados
            logger.error(f"Error al registrar usuario: {e}")
            raise RuntimeError(f"Error al registrar usuario: {str(e)}")
