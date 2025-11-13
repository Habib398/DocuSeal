import re
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


class EmailValidator:
    """
    Validador para requisitos de envío de correos electrónicos.
    Verifica que se cumplan todas las condiciones antes de enviar.
    """
    
    # Patrón regex para validar formato de email
    PATRON_EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """
        Valida que un email tenga formato correcto.
        """
        if not email:
            return False, "Email vacío"
        
        email = email.strip()
        
        if not re.match(EmailValidator.PATRON_EMAIL, email):
            return False, f"Formato de email inválido: {email}"
        
        return True, ""
    
    @staticmethod
    def validar_emails(emails: List[str]) -> Tuple[bool, str]:
        """
        Valida una lista de emails.
        """
        if not emails:
            return False, "Lista de emails vacía"
        
        for email in emails:
            es_valido, error = EmailValidator.validar_email(email)
            if not es_valido:
                return False, error
        
        return True, ""
    
    @staticmethod
    def validar_requisitos(
        solicito_correo: bool,
        destinatarios: List[str] = None,
        timbrado_exitoso: bool = True
    ) -> Tuple[bool, str]:
        """
        Valida que se cumplan todos los requisitos para enviar correo:
        1. solicito_correo debe ser True
        2. Debe haber al menos un destinatario
        3. Timbrado debe haber sido exitoso
        """
        # Validación 1: ¿Se solicitó correo?
        if not solicito_correo:
            logger.info("Envío de correo no solicitado")
            return False, "El envío de correo no fue solicitado"
        
        # Validación 2: ¿Hay destinatarios?
        if not destinatarios:
            logger.warning("Se solicitó correo pero no hay destinatarios")
            return False, "Se solicitó correo pero no se proporcionaron destinatarios"
        
        if not isinstance(destinatarios, list):
            return False, "Los destinatarios deben ser una lista"
        
        # Validación 3: ¿La lista está vacía?
        destinatarios_filtrados = [d for d in destinatarios if d]
        if not destinatarios_filtrados:
            logger.warning("Lista de destinatarios vacía")
            return False, "La lista de destinatarios está vacía"
        
        # Validación 4: ¿Todos los emails son válidos?
        todos_validos, error_email = EmailValidator.validar_emails(destinatarios_filtrados)
        if not todos_validos:
            logger.warning(f"Email inválido: {error_email}")
            return False, f"Email inválido: {error_email}"
        
        # Validación 5: ¿El timbrado fue exitoso?
        if not timbrado_exitoso:
            logger.info("No se envía correo porque el timbrado no fue exitoso")
            return False, "El correo no se envía porque el timbrado no fue exitoso"
        
        logger.info(f"Todos los requisitos cumplidos. Enviando a {len(destinatarios_filtrados)} destinatarios")
        return True, ""
    
    @staticmethod
    def validar_asunto(asunto: str) -> Tuple[bool, str]:
        """
        Valida que el asunto sea válido.
        """
        if not asunto:
            return False, "Asunto vacío"
        
        asunto = asunto.strip()
        
        if len(asunto) < 3:
            return False, "Asunto muy corto (mínimo 3 caracteres)"
        
        if len(asunto) > 255:
            return False, "Asunto muy largo (máximo 255 caracteres)"
        
        return True, ""
    
    @staticmethod
    def validar_cuerpo(cuerpo: str) -> Tuple[bool, str]:
        """
        Valida que el cuerpo del correo sea válido.
        """
        if not cuerpo:
            return False, "Cuerpo del correo vacío"
        
        cuerpo = cuerpo.strip()
        
        if len(cuerpo) < 5:
            return False, "Cuerpo muy corto (mínimo 5 caracteres)"
        
        return True, ""
