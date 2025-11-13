import logging
from typing import Dict, List, Union, Optional

from Business.Configuration.ConfiguracionCorreo import ConfiguracionCorreo
from Business.Services.EmailService import EmailService
from Business.Services.EmailValidator import EmailValidator

logger = logging.getLogger(__name__)

class Correo:
    """
    Clase para orquestar el envío de correos electrónicos.
    """
    
    def __init__(self, config: ConfiguracionCorreo = None):
        """
        Inicializa la clase Correo con las dependencias necesarias.
        """
        try:
            # Si no se proporciona config, intentar crear una
            if config is None:
                config = ConfiguracionCorreo()
            
            self.config = config
            self.email_service = EmailService(config)
            self.validator = EmailValidator()
            
            logger.info("Correo inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar Correo: {str(e)}")
            raise
    
    def GenerarCorreo(
        self,
        destinatarios: Union[str, List[str]],
        asunto: str,
        cuerpo: str,
        solicito_correo: bool = True,
        timbrado_exitoso: bool = True
    ) -> Dict[str, Union[bool, str]]:
        """
        Genera y valida el correo antes de enviarlo.
        """
        try:
            # Convertir email único a lista si es necesario
            if isinstance(destinatarios, str):
                destinatarios = [destinatarios]
            
            logger.info(f"Validando requisitos para correo a {len(destinatarios)} destinatario(s)")
            
            # Validación 1: Requisitos principales
            cumple_requisitos, error_requisitos = self.validator.validar_requisitos(
                solicito_correo=solicito_correo,
                destinatarios=destinatarios,
                timbrado_exitoso=timbrado_exitoso
            )
            
            if not cumple_requisitos:
                logger.warning(f"Requisitos no cumplidos: {error_requisitos}")
                return {
                    'valido': False,
                    'mensaje': 'No se enviará correo',
                    'error': error_requisitos
                }
            
            # Validación 2: Asunto
            asunto_valido, error_asunto = self.validator.validar_asunto(asunto)
            if not asunto_valido:
                logger.warning(f"Asunto inválido: {error_asunto}")
                return {
                    'valido': False,
                    'mensaje': 'Asunto inválido',
                    'error': error_asunto
                }
            
            # Validación 3: Cuerpo
            cuerpo_valido, error_cuerpo = self.validator.validar_cuerpo(cuerpo)
            if not cuerpo_valido:
                logger.warning(f"Cuerpo inválido: {error_cuerpo}")
                return {
                    'valido': False,
                    'mensaje': 'Cuerpo inválido',
                    'error': error_cuerpo
                }
            
            # Todas las validaciones pasaron
            logger.info("Todas las validaciones de correo pasaron")
            return {
                'valido': True,
                'mensaje': 'Correo listo para enviar',
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Error al generar correo: {str(e)}"
            logger.error(error_msg)
            return {
                'valido': False,
                'mensaje': 'Error al validar correo',
                'error': error_msg
            }
    
    def EnviarCorreo(
        self,
        para: Union[str, List[str]],
        asunto: str,
        cuerpo: str,
        solicito_correo: bool = True,
        timbrado_exitoso: bool = True,
        xml_content: Optional[bytes] = None,
        pdf_bytes: Optional[bytes] = None
    ) -> Dict[str, Union[bool, str]]:
        """
        Valida y envía un correo electrónico con soporte para adjuntos.
        
        Args:
            para: Email o lista de emails destinatarios
            asunto: Asunto del correo
            cuerpo: Cuerpo del correo
            solicito_correo: Si el usuario solicitó correo
            timbrado_exitoso: Si el timbrado fue exitoso
            xml_content: Contenido XML como bytes (opcional)
            pdf_bytes: Contenido PDF como bytes (opcional)
        """
        try:
            # Primero generar y validar
            resultado_validacion = self.GenerarCorreo(
                destinatarios=para,
                asunto=asunto,
                cuerpo=cuerpo,
                solicito_correo=solicito_correo,
                timbrado_exitoso=timbrado_exitoso
            )
            
            # Si no es válido, retornar sin intentar enviar
            if not resultado_validacion['valido']:
                return {
                    'exitoso': False,
                    'mensaje': resultado_validacion['mensaje'],
                    'error': resultado_validacion['error']
                }
            
            # Convertir a lista si es necesario
            if isinstance(para, str):
                para = [para]
            
            logger.info(f"Enviando correo a {len(para)} destinatario(s)...")
            
            # Enviar el correo CON ADJUNTOS
            resultado_envio = self.email_service.enviar_email(
                para=para,
                asunto=asunto,
                cuerpo=cuerpo,
                conectar_automatico=True,
                xml_content=xml_content,
                pdf_bytes=pdf_bytes
            )
            
            if resultado_envio['exitoso']:
                logger.info(f"Correo enviado exitosamente: {resultado_envio['mensaje']}")
            else:
                logger.error(f"Error al enviar correo: {resultado_envio['error']}")
            
            return resultado_envio
            
        except Exception as e:
            error_msg = f"Error inesperado al enviar correo: {str(e)}"
            logger.error(error_msg)
            return {
                'exitoso': False,
                'mensaje': 'Error al enviar correo',
                'error': error_msg
            }
    
    def __repr__(self):
        """Representación en string"""
        return f"Correo(config={self.config})"
