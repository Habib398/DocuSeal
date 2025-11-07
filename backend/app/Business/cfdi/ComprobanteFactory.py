import logging
from typing import Dict, Any, Union
from .Comprobantes.Ingreso import ComprobanteIngreso
from .Comprobantes.Traslados import ComprobanteTraslado
from .Comprobantes.Pago import ComprobantePago

logger = logging.getLogger(__name__)


class ComprobanteFactory:

    _TIPO_CLASSES = {
        "I": ComprobanteIngreso,
        "T": ComprobanteTraslado,
        "P": ComprobantePago
        # "E": ComprobanteEgreso,  # Implementar cuando se requiera
        # "N": ComprobantaNomina,   # Implementar cuando se requiera
    }
    
    @classmethod
    def crear_comprobante(cls, datos_json: Dict[str, Any]) -> Union[ComprobanteIngreso, ComprobanteTraslado, ComprobantePago]:

        comprobante_data = datos_json.get("cfdi:Comprobante", datos_json)
        tipo = comprobante_data.get("TipoDeComprobante", "I")
        
        logger.info(f"ComprobanteFactory: Detectado TipoDeComprobante = '{tipo}'")
        
        # Buscar la clase correspondiente
        clase_comprobante = cls._TIPO_CLASSES.get(tipo)
        
        if clase_comprobante is None:
            # Verificar si es un tipo válido pero no implementado
            tipos_validos = ["E", "N"]
            if tipo in tipos_validos:
                error_msg = f"TipoDeComprobante '{tipo}' es válido pero aún no está implementado"
                logger.error(error_msg)
                raise NotImplementedError(error_msg)
            else:
                error_msg = f"TipoDeComprobante '{tipo}' no es válido. Tipos válidos: I, T, P, E, N"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        # Crear y retornar instancia
        logger.info(f"Creando instancia de {clase_comprobante.__name__}")
        return clase_comprobante(datos_json)
    
    @classmethod
    def procesar_comprobante(cls, datos_json: Dict[str, Any]) -> Dict[str, Any]:
        
        try:
            # Crear comprobante
            comprobante = cls.crear_comprobante(datos_json)
            
            # Validar
            resultado_validacion = comprobante.validar()
            
            # Si la validación pasa, generar XML
            if resultado_validacion["valido"]:
                xml_generado = comprobante.generar_xml()
                return {
                    "valido": True,
                    "xml": xml_generado,
                    "errores": [],
                    "warnings": resultado_validacion["warnings"]
                }
            else:
                return {
                    "valido": False,
                    "xml": None,
                    "errores": resultado_validacion["errores"],
                    "warnings": resultado_validacion["warnings"]
                }
                
        except (ValueError, NotImplementedError) as e:
            logger.exception(f"Error al procesar comprobante: {str(e)}")
            return {
                "valido": False,
                "xml": None,
                "errores": [{
                    "tipo": "error",
                    "codigo": "FACTORY_ERROR",
                    "mensaje": str(e)
                }],
                "warnings": []
            }
        except Exception as e:
            return {
                "valido": False,
                "xml": None,
                "errores": [{
                    "tipo": "error",
                    "codigo": "UNEXPECTED_ERROR",
                    "mensaje": f"Error inesperado: {str(e)}"
                }],
                "warnings": []
            }


__all__ = ["ComprobanteFactory"]
