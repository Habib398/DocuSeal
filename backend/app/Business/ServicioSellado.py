import logging
from typing import Dict, Any
from .SellarXML import SellarXML
from .cfdi.ComprobanteFactory import ComprobanteFactory

logger = logging.getLogger(__name__)


class ServicioSellado:
    """
    Servicio para operaciones de sellado de CFDI desde XML o estructura JSON.
    """
    
    @staticmethod
    def sellar(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sella un CFDI recibido como:
        - "xml": string XML (sellado directo)
        - "datosXML": estructura JSON (validación + generación + sellado)
        Requiere "claveUsuario" para obtener certificados de la BD.
        """

        # Validar claveUsuario
        if not data.get('claveUsuario'):
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "SELL001",
                    "mensaje": "Falta el campo 'claveUsuario' en la petición"
                }]
            }

        # Verificar que venga uno de los dos formatos
        xml_input = data.get('xml')
        json_input = data.get('datosXML')
        
        if not xml_input and not json_input:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "SELL002",
                    "mensaje": "Debe proporcionar 'xml' (string XML) o 'datosXML' (estructura JSON)"
                }]
            }
        
        # XML directo - sellar sin procesar
        if xml_input and isinstance(xml_input, str):
            logger.info(f"Sellando XML string directo (longitud: {len(xml_input)} caracteres)")
            return SellarXML.sellar_cfdi(data)

        # JSON - usar Factory para validar, generar XML y sellar
        elif json_input and isinstance(json_input, dict):
            logger.info("Procesando JSON con ComprobanteFactory según TipoDeComprobante")
            
            try:
                # Procesar con Factory (valida + genera XML)
                resultado_factory = ComprobanteFactory.procesar_comprobante(json_input)
                
                # Si hay errores de validación, retornar inmediatamente
                if not resultado_factory["valido"]:
                    logger.error(f"Validación fallida: {resultado_factory['errores']}")
                    return {
                        "error": "Validación de comprobante fallida",
                        "errores": resultado_factory["errores"],
                        "warnings": resultado_factory["warnings"]
                    }
                
                # Si la validación pasó, sellar el XML generado
                xml_generado = resultado_factory["xml"]
                logger.info(f"XML generado exitosamente (longitud: {len(xml_generado)} caracteres)")
                
                # Preparar data para sellado (incluir claveUsuario)
                data_para_sellar = {
                    "xml": xml_generado,
                    "claveUsuario": data.get("claveUsuario"),
                    "enviarCorreo": data.get("enviarCorreo", False),
                    "generarPDF": data.get("generarPDF", False)
                }
                
                # Sellar el XML
                resultado_sellado = SellarXML.sellar_cfdi(data_para_sellar)
                
                # Agregar warnings de validación al resultado (si los hay)
                if resultado_factory["warnings"] and isinstance(resultado_sellado, dict):
                    resultado_sellado["warnings"] = resultado_factory["warnings"]
                
                return resultado_sellado
                
            except (ValueError, NotImplementedError) as e:
                logger.exception(f"Error al procesar comprobante con Factory: {str(e)}")
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SELL003",
                        "mensaje": str(e),
                        "detalle": "Error en ComprobanteFactory"
                    }]
                }
            except Exception as e:
                logger.exception(f"Error inesperado al procesar JSON: {str(e)}")
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SELL004",
                        "mensaje": f"Error inesperado: {str(e)}",
                        "detalle": "Error en procesamiento de JSON"
                    }]
                }
        
        # Fallback: intentar sellado tradicional
        logger.warning("Fallback a SellarXML tradicional")
        return SellarXML.sellar_cfdi(data)
