"""
ServicioTimbrado.py - Service Layer para operaciones de timbrado de CFDI
Solo acepta XML en formato string (xml)
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
        Usa claveUsuario para obtener el certificado de la BD.
        """
        logger.info("Iniciando proceso de timbrado desde XML")
        
        # Extraer XML y claveUsuario
        xml_input = data.get('xml')
        clave_usuario = data.get('claveUsuario')
        
        if not xml_input:
            return {"error": "Falta campo 'xml' en el cuerpo de la petición"}
        
        if not clave_usuario:
            return {"error": "Falta campo 'claveUsuario' en el cuerpo de la petición"}
        
        # Obtener certificado de la base de datos usando claveUsuario
        from .Configuration.ConfiguracionCertificados import ConfiguracionCertificados
        from DB.DBManager import DBManager
        
        try:
            db_manager = DBManager()
            config_cert = ConfiguracionCertificados(db_manager)
            certificado = config_cert.obtener_por_clave_usuario(clave_usuario)
            
            if not certificado:
                logger.error(f"No se encontró certificado con claveUsuario: {clave_usuario}")
                return {
                    "error": "Certificado no encontrado",
                    "detalle": f"No se encontró certificado con claveUsuario {clave_usuario} en la base de datos"
                }
            
            # Obtener credenciales PAC y noCertificado de la BD
            usuario_pac = certificado.get('usuarioPAC')
            contrasena_pac = certificado.get('contrasenaPAC')
            no_certificado = certificado.get('noCertificado')
            
            if not usuario_pac or not contrasena_pac:
                logger.error(f"Certificado {clave_usuario} no tiene credenciales PAC completas")
                return {
                    "error": "Credenciales PAC incompletas",
                    "detalle": f"El certificado {clave_usuario} no tiene usuarioPAC o contrasenaPAC configurados"
                }
            
            if not no_certificado:
                logger.error(f"Certificado {clave_usuario} no tiene noCertificado")
                return {
                    "error": "NoCertificado faltante",
                    "detalle": f"El certificado {clave_usuario} no tiene noCertificado configurado"
                }
            
            logger.info(f"Certificado obtenido de la BD con claveUsuario: {clave_usuario}")
            logger.info(f"NoCertificado asignado desde BD: {no_certificado}")
            
        except Exception as e:
            logger.error(f"Error al obtener certificado de la BD: {str(e)}")
            return {
                "error": "Error al acceder a la base de datos",
                "detalle": f"No se pudo obtener el certificado: {str(e)}"
            }
        
        # Actualizar NoCertificado en el XML con el valor de la BD
        from lxml import etree
        try:
            xml_tree = etree.fromstring(xml_input.encode('utf-8'))
            xml_tree.set('NoCertificado', no_certificado)
            xml_input = etree.tostring(xml_tree, encoding='unicode')
            logger.info(f"NoCertificado actualizado en XML: {no_certificado}")
        except Exception as e:
            logger.error(f"Error al actualizar NoCertificado en XML: {str(e)}")
            return {
                "error": "Error al procesar XML",
                "detalle": f"No se pudo actualizar NoCertificado: {str(e)}"
            }
        
        pruebas = data.get('pruebas', True)
        
        # Ejecutar timbrado directamente
        logger.info(f"Timbrando XML con PAC (pruebas={pruebas})")
        return TimbradoService.timbrar_cfdi(xml_input, usuario_pac, contrasena_pac, pruebas)
