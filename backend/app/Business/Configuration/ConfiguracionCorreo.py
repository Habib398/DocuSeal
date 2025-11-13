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
        Busca el .env en la raíz del proyecto
        """
        # Cargar variables de entorno desde .env
        # Busca el archivo .env en la raíz del proyecto (5 niveles arriba de este archivo)
        env_path = Path(__file__).resolve().parent.parent.parent.parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        
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