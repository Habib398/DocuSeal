import os
from dotenv import load_dotenv
from pathlib import Path


class ConfiguracionCorreo:
    """
    Clase para gestionar la configuración de correo electrónico.
    Lee las credenciales desde variables de entorno (.env)
    """
    
    def __init__(self):
        """
        Inicializa la configuración leyendo del archivo .env
        Busca el .env en la raíz del proyecto DocuSeal
        """
        # Cargar variables de entorno desde .env
        # Busca el archivo .env en múltiples ubicaciones, priorizando la raíz del proyecto:
        # ConfiguracionCorreo.py está en: backend/app/Business/Configuration/ (5 niveles desde raíz)
        # 1. Raíz del proyecto de DocuSeal (5 niveles arriba)
        # 2. Working directory actual
        # 3. Parent del working directory
        # 4. Carpeta del usuario (AppData)
        
        env_paths = [
            Path(__file__).resolve().parent.parent.parent.parent.parent / '.env',  # 5 niveles arriba a raíz del proyecto
            Path.cwd() / '.env',  # Working directory
            Path.cwd().parent / '.env',  # Parent de working directory
            Path.home() / 'DocuSeal' / '.env',  # Home/DocuSeal
        ]
        
        env_found = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                env_found = True
                break
        
        if not env_found:
            # Si no encuentra .env, intenta cargar desde variables de entorno del sistema
            load_dotenv()
        
        # Leer configuración desde variables de entorno
        self.host = os.getenv('EMAIL_SMTP_SERVER')
        self.port = int(os.getenv('EMAIL_SMTP_PORT', 465))
        self.username = os.getenv('EMAIL_SENDER')
        self.password = os.getenv('EMAIL_PASSWORD')
        self.use_tls = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
        
        # Validar que las credenciales estén disponibles
        self._validar_configuracion()
    
    def _validar_configuracion(self):
        """
        Valida que todas las credenciales requeridas estén presentes.
        Lanza una excepción si alguna está faltando.
        """
        campos_requeridos = {
            'EMAIL_SMTP_SERVER': self.host,
            'EMAIL_SMTP_PORT': self.port,
            'EMAIL_SENDER': self.username,
            'EMAIL_PASSWORD': self.password,
        }
        
        campos_faltantes = [campo for campo, valor in campos_requeridos.items() if not valor]
        
        if campos_faltantes:
            raise ValueError(
                f"Falta configurar las siguientes variables de entorno: {', '.join(campos_faltantes)}. "
                f"Por favor, verifica el archivo .env en la raíz del proyecto."
            )
    
    def Credenciales(self):
        """
        Retorna un diccionario con todas las credenciales configuradas.
        
        Returns:
            dict: Diccionario con host, port, username, password, use_tls
        """
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "use_tls": self.use_tls
        }
    
    def __repr__(self):
        """Representación en string (sin exponer la contraseña)"""
        return (
            f"ConfiguracionCorreo(host={self.host}, port={self.port}, "
            f"username={self.username}, use_tls={self.use_tls})"
        )