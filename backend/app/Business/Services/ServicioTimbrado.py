"""
ServicioTimbrado.py - Service Layer para operaciones de timbrado de CFDI
Solo acepta XML en formato string (xml)
"""

import logging
from typing import Dict, Any
from Business.Timbrado import TimbradoService

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
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "TIMB001",
                    "mensaje": "Falta campo 'xml' en el cuerpo de la petición"
                }]
            }
        
        if not clave_usuario:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "TIMB002",
                    "mensaje": "Falta campo 'claveUsuario' en el cuerpo de la petición"
                }]
            }
        
        # Obtener certificado de la base de datos usando claveUsuario
        from Business.Configuration.ConfiguracionCertificados import ConfiguracionCertificados
        from DB.DBManager import DBManager
        
        try:
            db_manager = DBManager()
            config_cert = ConfiguracionCertificados(db_manager)
            certificado = config_cert.obtener_por_clave_usuario(clave_usuario)
            
            if not certificado:
                logger.error(f"No se encontró certificado con claveUsuario: {clave_usuario}")
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "TIMB003",
                        "mensaje": "Certificado no encontrado",
                        "detalle": f"No se encontró certificado con claveUsuario {clave_usuario} en la base de datos"
                    }]
                }
            
            # Obtener credenciales PAC y noCertificado de la BD
            usuario_pac = certificado.get('usuarioPAC')
            contrasena_pac = certificado.get('contrasenaPAC')
            no_certificado = certificado.get('noCertificado')
            
            if not usuario_pac or not contrasena_pac:
                logger.error(f"Certificado {clave_usuario} no tiene credenciales PAC completas")
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "TIMB004",
                        "mensaje": "Credenciales PAC incompletas",
                        "detalle": f"El certificado {clave_usuario} no tiene usuarioPAC o contrasenaPAC configurados"
                    }]
                }
            
            if not no_certificado:
                logger.error(f"Certificado {clave_usuario} no tiene noCertificado")
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "TIMB005",
                        "mensaje": "NoCertificado faltante",
                        "detalle": f"El certificado {clave_usuario} no tiene noCertificado configurado"
                    }]
                }
            
            logger.info(f"Certificado obtenido de la BD con claveUsuario: {clave_usuario}")
            logger.info(f"NoCertificado asignado desde BD: {no_certificado}")
            
        except Exception as e:
            logger.error(f"Error al obtener certificado de la BD: {str(e)}")
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "TIMB006",
                    "mensaje": "Error al acceder a la base de datos",
                    "detalle": f"No se pudo obtener el certificado: {str(e)}"
                }]
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
                "errores": [{
                    "tipo": "error",
                    "codigo": "TIMB007",
                    "mensaje": "Error al procesar XML",
                    "detalle": f"No se pudo actualizar NoCertificado: {str(e)}"
                }]
            }
        
        # Obtener el modo de pruebas desde el certificado
        pruebas = certificado.get('pruebas', True)
        generar_pdf = data.get('generarPDF', False)
        
        # Ejecutar timbrado directamente
        logger.info(f"Timbrando XML con PAC (pruebas={pruebas})")
        resultado_timbrado = TimbradoService.timbrar_cfdi(xml_input, usuario_pac, contrasena_pac, pruebas)
        
        # Generar PDF si se solicita y el timbrado fue exitoso
        if generar_pdf and "errores" not in resultado_timbrado:
            logger.info("Generando PDF después del timbrado")
            try:
                from Business.PDF import PDF
                uuid = resultado_timbrado.get("uuid", "temp")
                xml_timbrado = resultado_timbrado.get("cuerpo", xml_input)
                
                # Generar PDF desde el XML timbrado
                pdf_info = PDF.generar_desde_datos(xml_timbrado, uuid)
                resultado_timbrado.update(pdf_info)
                logger.info("PDF generado exitosamente")
            except Exception as e:
                logger.error(f"Error al generar PDF: {str(e)}")
                resultado_timbrado["html_generado"] = False
                resultado_timbrado["pdf_error"] = str(e)
        elif not generar_pdf:
            resultado_timbrado["html_generado"] = False
        
        return resultado_timbrado
