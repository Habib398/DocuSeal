import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Union, Optional


# Configurar logging
logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para enviar correos electrónicos usando SMTP.
    Maneja la conexión al servidor de correo y el envío de emails.
    """

    def __init__(self, config):
        """
        Inicializa el servicio de email con la configuración proporcionada.
        """
        self.config = config
        self.server = None
        self.conectado = False
        
        # Obtener credenciales de la configuración
        credenciales = config.Credenciales()
        self.host = credenciales['host']
        self.port = credenciales['port']
        self.username = credenciales['username']
        self.password = credenciales['password']
        self.use_tls = credenciales['use_tls']
        
        logger.info(f"EmailService inicializado para {self.host}:{self.port}")

    def conectar_servidor(self) -> Dict[str, Union[bool, str]]:
        """
        Conecta al servidor SMTP.
        """
        try:
            logger.info(f"Intentando conectar a {self.host}:{self.port}...")
            
            # Crear contexto SSL seguro
            context = ssl.create_default_context()
            
            # Para puerto 465: usar SMTP_SSL
            # Para puerto 587: usar SMTP + starttls()
            if self.port == 465:
                logger.info("Usando SMTP_SSL para puerto 465...")
                self.server = smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=10)
            else:
                logger.info("Usando SMTP con starttls()...")
                self.server = smtplib.SMTP(self.host, self.port, timeout=10)
                if self.use_tls:
                    logger.info("Iniciando conexión TLS...")
                    self.server.starttls(context=context)
            
            # Autenticar con credenciales
            logger.info(f"Autenticando como {self.username}...")
            self.server.login(self.username, self.password)
            
            self.conectado = True
            mensaje = f"Conexión exitosa a {self.host}:{self.port}"
            logger.info(mensaje)
            
            return {
                'exitoso': True,
                'mensaje': mensaje,
                'error': None
            }
            
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP: {str(e)}"
            logger.error(error_msg)
            self.conectado = False
            return {
                'exitoso': False,
                'mensaje': 'Error al conectar con el servidor SMTP',
                'error': error_msg
            }
        except ssl.SSLError as e:
            error_msg = f"Error SSL: {str(e)}"
            logger.error(error_msg)
            self.conectado = False
            return {
                'exitoso': False,
                'mensaje': 'Error de seguridad SSL/TLS',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg)
            self.conectado = False
            return {
                'exitoso': False,
                'mensaje': 'Error al conectar al servidor',
                'error': error_msg
            }

    def desconectar_servidor(self) -> None:
        """
        Desconecta del servidor SMTP.
        """
        try:
            if self.server:
                self.server.quit()
                self.conectado = False
                logger.info("Desconectado del servidor SMTP")
        except Exception as e:
            logger.warning(f"Error al desconectar: {str(e)}")
            if self.server:
                try:
                    self.server.close()
                except:
                    pass
            self.conectado = False

    def enviar_email(
        self, 
        para: Union[str, List[str]], 
        asunto: str, 
        cuerpo: str,
        conectar_automatico: bool = True,
        xml_content: Optional[bytes] = None,
        pdf_bytes: Optional[bytes] = None,
        uuid: Optional[str] = None
    ) -> Dict[str, Union[bool, str]]:
        """
        Envía un correo electrónico con soporte para adjuntos XML y PDF.
        """
        try:
            # Convertir un email a lista si es necesario
            if isinstance(para, str):
                para = [para]
            
            # Validaciones básicas
            if not para:
                raise ValueError("Debe proporcionar al menos un destinatario")
            
            if not asunto:
                raise ValueError("El asunto del correo es requerido")
            
            if not cuerpo:
                raise ValueError("El cuerpo del correo es requerido")
            
            # Conectar si no está conectado
            if not self.conectado and conectar_automatico:
                resultado_conexion = self.conectar_servidor()
                if not resultado_conexion['exitoso']:
                    return resultado_conexion
            
            # Validar que esté conectado
            if not self.conectado:
                return {
                    'exitoso': False,
                    'mensaje': 'No hay conexión con el servidor SMTP',
                    'error': 'Llama a conectar_servidor() primero'
                }
            
            # Crear mensaje MIME
            mensaje = MIMEMultipart('mixed')
            mensaje['From'] = self.username
            mensaje['To'] = ', '.join(para)
            mensaje['Subject'] = asunto
            
            # Agregar cuerpo del correo como texto plano
            parte_texto = MIMEText(cuerpo, 'plain', 'utf-8')
            mensaje.attach(parte_texto)
            
            # Adjuntar XML si se proporciona
            if xml_content:
                try:
                    nombre_xml = f'{uuid}.xml'
                    self._adjuntar_archivo(
                        mensaje=mensaje,
                        contenido=xml_content,
                        nombre_archivo=nombre_xml,
                        tipo_mime='application/xml'
                    )
                    logger.info("Adjunto XML agregado al correo")
                except Exception as e:
                    logger.warning(f"Error al adjuntar XML: {str(e)}")
            
            # Adjuntar PDF si se proporciona
            if pdf_bytes:
                try:
                    nombre_pdf = f'{uuid}.pdf'
                    self._adjuntar_archivo(
                        mensaje=mensaje,
                        contenido=pdf_bytes,
                        nombre_archivo=nombre_pdf,
                        tipo_mime='application/pdf'
                    )
                    logger.info("Adjunto PDF agregado al correo")
                except Exception as e:
                    logger.warning(f"Error al adjuntar PDF: {str(e)}")
            
            # Enviar correo
            logger.info(f"Enviando correo a {para} con asunto: {asunto}")
            self.server.sendmail(self.username, para, mensaje.as_string())
            
            mensaje_exito = f"Correo enviado exitosamente a {', '.join(para)}"
            logger.info(mensaje_exito)
            
            return {
                'exitoso': True,
                'mensaje': mensaje_exito,
                'error': None
            }
            
        except ValueError as e:
            error_msg = f"Error de validación: {str(e)}"
            logger.error(error_msg)
            return {
                'exitoso': False,
                'mensaje': 'Error en los parámetros del correo',
                'error': error_msg
            }
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP al enviar: {str(e)}"
            logger.error(error_msg)
            return {
                'exitoso': False,
                'mensaje': 'Error al enviar el correo',
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg)
            return {
                'exitoso': False,
                'mensaje': 'Error desconocido al enviar el correo',
                'error': error_msg
            }


    def _adjuntar_archivo(
        self, 
        mensaje: MIMEMultipart, 
        contenido: bytes, 
        nombre_archivo: str,
        tipo_mime: str = 'application/octet-stream'
    ) -> None:
        """
        Adjunta un archivo binario al mensaje MIME.
        
        Args:
            mensaje: Objeto MIMEMultipart donde agregar el adjunto
            contenido: Contenido del archivo en bytes
            nombre_archivo: Nombre del archivo a mostrar
            tipo_mime: Tipo MIME del archivo (ej: application/pdf, application/xml)
        """
        try:
            # Crear parte MIME base para el archivo binario
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(contenido)
            
            # Codificar el contenido en base64
            encoders.encode_base64(parte)
            
            # Agregar headers para indicar que es un adjunto
            parte.add_header(
                'Content-Disposition',
                f'attachment; filename= {nombre_archivo}'
            )
            
            # Agregar la parte al mensaje
            mensaje.attach(parte)
            
            logger.info(f"Archivo '{nombre_archivo}' adjuntado al correo")
            
        except Exception as e:
            logger.error(f"Error al adjuntar archivo '{nombre_archivo}': {str(e)}")
            raise

    def __del__(self):
        """
        Destructor: Asegura que la conexión se cierre al eliminar el objeto.
        """
        self.desconectar_servidor()