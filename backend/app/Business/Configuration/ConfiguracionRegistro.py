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
        """
        Inicializa el servicio de registro.
        
        Args:
            db_manager: Instancia de DBManager para operaciones de BD
        """
        self.db_manager = db_manager
    
    def validar_passwords(self, password: str, confirm_password: str) -> tuple[bool, str]:
        """
        Valida que las contraseñas coincidan y cumplan requisitos mínimos.
        
        Args:
            password: Contraseña ingresada
            confirm_password: Confirmación de contraseña
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if password != confirm_password:
            return False, "Las contraseñas no coinciden"
        
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        return True, ""
    
    def validar_fortaleza_password(self, password: str) -> tuple[bool, str]:
        """
        Valida la fortaleza de la contraseña (opcional, se puede extender).
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        # Validaciones adicionales que se pueden agregar:
        # - Al menos una mayúscula
        # - Al menos un número
        # - Al menos un carácter especial
        
        # Por ahora solo verificamos longitud mínima
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        return True, ""
    
    def hashear_password(self, password: str) -> str:
        """
        Hashea la contraseña usando bcrypt.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Contraseña hasheada
            
        Raises:
            RuntimeError: Si bcrypt no está disponible
        """
        if bcrypt is None:
            raise RuntimeError("bcrypt no está instalado. Instale con: pip install bcrypt")
        
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        return password_hash.decode('utf-8')
    
    def verificar_email_disponible(self, email: str) -> tuple[bool, str]:
        """
        Verifica si el email ya está registrado.
        
        Args:
            email: Email a verificar
            
        Returns:
            Tupla (esta_disponible, mensaje_error)
        """
        try:
            usuario_existente = self.db_manager.get_usuario_by_email(email)
            if usuario_existente:
                return False, "El email ya está registrado"
            return True, ""
        except Exception as e:
            logger.error(f"Error verificando email: {e}")
            return False, f"Error al verificar email: {str(e)}"
    
    def registrar_usuario(self, datos: UsuarioRegistroRequest) -> Dict[str, Any]:
        """
        Procesa el registro completo de un usuario.
        
        Args:
            datos: Datos del usuario a registrar
            
        Returns:
            Diccionario con resultado del registro
            
        Raises:
            ValueError: Si las validaciones fallan
            RuntimeError: Si hay error en el proceso
        """
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
