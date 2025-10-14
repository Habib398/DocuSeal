"""
ServicioTimbrado.py - Service Layer para operaciones de timbrado de CFDI
Solo acepta XML en formato string (datos_xml)
"""

import logging
from typing import Dict, Any
from .Timbrado import TimbradoService

logger = logging.getLogger(__name__)


class ServicioTimbrado:
    """
    Servicio para operaciones de timbrado de CFDI desde XML.
    """
    
    @staticmethod
    def timbrar(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Timbra un CFDI recibido como XML usando credenciales del PAC.
        """
        logger.info("Iniciando proceso de timbrado desde XML")
        
        # Extraer XML
        xml_input = data.get('datos_xml')
        if not xml_input:
            return {"error": "Falta campo 'datos_xml' en el cuerpo de la petición"}
        
        # Extraer NoCertificado del XML para obtener credenciales PAC de la BD
        from lxml import etree
        try:
            xml_tree = etree.fromstring(xml_input.encode('utf-8'))
            no_certificado = xml_tree.get('NoCertificado')
            logger.info(f"NoCertificado extraído del XML: {no_certificado}")
        except Exception as e:
            logger.error(f"Error al parsear XML para extraer NoCertificado: {str(e)}")
            return {
                "error": "Error al procesar XML",
                "detalle": f"No se pudo extraer NoCertificado: {str(e)}"
            }
        
        # Obtener credenciales PAC de la base de datos
        from .Configuration.ConfiguracionCertificados import ConfiguracionCertificados
        from DB.DBManager import DBManager
        
        try:
            db_manager = DBManager()
            config_cert = ConfiguracionCertificados(db_manager)
            certificado = config_cert.obtener_por_numero(no_certificado)
            
            if not certificado:
                logger.error(f"No se encontró certificado con NoCertificado: {no_certificado}")
                return {
                    "error": "Certificado no encontrado",
                    "detalle": f"No se encontró certificado con NoCertificado {no_certificado} en la base de datos"
                }
            
            usuario_pac = certificado.get('usuarioPAC')
            contrasena_pac = certificado.get('contrasenaPAC')
            
            if not usuario_pac or not contrasena_pac:
                logger.error(f"Certificado {no_certificado} no tiene credenciales PAC completas")
                return {
                    "error": "Credenciales PAC incompletas",
                    "detalle": f"El certificado {no_certificado} no tiene usuarioPAC o contrasenaPAC configurados"
                }
            
            logger.info(f"Credenciales PAC obtenidas de la BD para certificado {no_certificado}")
            
        except Exception as e:
            logger.error(f"Error al obtener credenciales PAC de la BD: {str(e)}")
            return {
                "error": "Error al acceder a la base de datos",
                "detalle": f"No se pudieron obtener las credenciales PAC: {str(e)}"
            }
        
        pruebas = data.get('pruebas', True)
        
        pruebas = data.get('pruebas', True)
        
        # Ejecutar timbrado directamente
        logger.info(f"Timbrando XML con PAC (pruebas={pruebas})")
        return TimbradoService.timbrar_cfdi(xml_input, usuario_pac, contrasena_pac, pruebas)
