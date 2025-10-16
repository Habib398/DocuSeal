"""
ServicioTimbrarSellar.py - Service Layer para operaciones completas de sellado y timbrado
Acepta:
- "xml": string XML
- "datosXML": estructura JSON (dict)
"""

import logging
from typing import Dict, Any
from .SellarXML import SellarXML
from .Timbrado import TimbradoService
from .PDF import PDF
from .PreferenciasCliente import PreferenciasCliente

logger = logging.getLogger(__name__)


class ServicioTimbrarSellar:
    """
    Servicio para operaciones completas de sellado y timbrado de CFDI desde XML.
    """
    
    @staticmethod
    def procesar(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un CFDI completo: sellado y timbrado.
        Acepta:
        - "xml": string XML
        - "datosXML": estructura JSON (dict)
        """
        logger.info("Iniciando proceso completo de timbrarSellar")
        
        # Validar que venga al menos uno de los dos formatos
        xml_input = data.get('xml')
        json_input = data.get('datosXML')
        
        if not xml_input and not json_input:
            return {"error": "Debe proporcionar 'xml' (string XML) o 'datosXML' (estructura JSON)"}
        
        if xml_input:
            logger.info(f"Procesando XML string (longitud: {len(xml_input)} caracteres)")
        else:
            logger.info("Procesando estructura JSON en 'datosXML'")
        
        # Sellado
        logger.info("Iniciando sellado")
        resultado_sellado = SellarXML.sellar_cfdi(data)
        if "error" in resultado_sellado:
            logger.error(f"Error en sellado: {resultado_sellado['error']}")
            return resultado_sellado
        
        xml_sellado = resultado_sellado["xml_con_sello"]
        cadena_original = resultado_sellado.get("cadena_original", "")
        logger.info("Sellado exitoso")
        
        # Extraer NoCertificado del XML sellado para obtener credenciales PAC de la BD
        from lxml import etree
        try:
            xml_tree = etree.fromstring(xml_sellado.encode('utf-8'))
            no_certificado = xml_tree.get('NoCertificado')
            logger.info(f"NoCertificado extraído del XML sellado: {no_certificado}")
        except Exception as e:
            logger.error(f"Error al parsear XML sellado para extraer NoCertificado: {str(e)}")
            return {
                "error": "Error al procesar XML sellado",
                "detalle": f"No se pudo extraer NoCertificado: {str(e)}",
                "xml_sellado": xml_sellado,
                "cadena_original": cadena_original
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
                    "detalle": f"No se encontró certificado con NoCertificado {no_certificado} en la base de datos",
                    "xml_sellado": xml_sellado,
                    "cadena_original": cadena_original
                }
            
            usuario_pac = certificado.get('usuarioPAC')
            contrasena_pac = certificado.get('contrasenaPAC')
            
            if not usuario_pac or not contrasena_pac:
                logger.error(f"Certificado {no_certificado} no tiene credenciales PAC completas")
                return {
                    "error": "Credenciales PAC incompletas",
                    "detalle": f"El certificado {no_certificado} no tiene usuarioPAC o contrasenaPAC configurados",
                    "xml_sellado": xml_sellado,
                    "cadena_original": cadena_original
                }
            
            logger.info(f"Credenciales PAC obtenidas de la BD para certificado {no_certificado}")
            
        except Exception as e:
            logger.error(f"Error al obtener credenciales PAC de la BD: {str(e)}")
            return {
                "error": "Error al acceder a la base de datos",
                "detalle": f"No se pudieron obtener las credenciales PAC: {str(e)}",
                "xml_sellado": xml_sellado,
                "cadena_original": cadena_original
            }
        
        pruebas = data.get("pruebas", True)
        
        # Timbrado
        logger.info(f"Iniciando timbrado con PAC (pruebas={pruebas})")
        resultado_timbrado = TimbradoService.timbrar_cfdi(
            xml_sellado,
            usuario_pac,
            contrasena_pac,
            pruebas
        )
        
        # Preparar respuesta
        respuesta = resultado_timbrado.copy()
        respuesta["cadena_original"] = cadena_original
        logger.info("Timbrado exitoso")
        
        # Generar PDF si se solicita
        preferencias = PreferenciasCliente.from_json(data)
        if preferencias.enviarPDF:
            logger.info("Generando PDF según solicitud del usuario")
            uuid = resultado_timbrado.get("uuid", "temp")
            pdf_info = PDF.generar_desde_datos(data, xml_sellado, cadena_original, uuid)
            logger.info("PDF generado exitosamente")
            respuesta.update(pdf_info)
        else:
            logger.info("Usuario no solicitó generación de PDF")
            respuesta["html_generado"] = False
        
        return respuesta
