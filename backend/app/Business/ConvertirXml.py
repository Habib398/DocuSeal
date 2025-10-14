
import logging
from typing import Union, Dict, Any
from lxml import etree
from satcfdi.cfdi import CFDI
from satcfdi.exceptions import CFDIError

logger = logging.getLogger(__name__)


class ConvertirXmlError(Exception):
    """Excepción personalizada para errores de conversión de XML"""
    pass


def parse_cfdi_from_string(xml_input: Union[str]) -> CFDI:
    """
    Parsea un XML de CFDI desde string o bytes y devuelve un objeto CFDI.
    """
    try:
        # Si es string, convertir a bytes para que lxml use la declaración de encoding
        if isinstance(xml_input, str):
            xml_bytes = xml_input.encode('utf-8')
        else:
            xml_bytes = xml_input
        
        # Parsear usando satcfdi
        cfdi = CFDI.from_string(xml_bytes)
        return cfdi
        
    except etree.XMLSyntaxError as e:
        error_msg = f"XML mal formado: {str(e)}"
        logger.error(error_msg)
        raise ConvertirXmlError(error_msg) from e
    
    except CFDIError as e:
        error_msg = f"Error en estructura CFDI: {str(e)}"
        logger.error(error_msg)
        raise ConvertirXmlError(error_msg) from e
    
    except Exception as e:
        error_msg = f"Error inesperado al parsear XML: {str(e)}"
        logger.error(error_msg)
        raise ConvertirXmlError(error_msg) from e


def extraer_carta_porte_desde_xml(xml_input: Union[str]) -> Dict[str, Any]:
    """
    Parsea el XML y extrae los datos del complemento CartaPorte si existe.
    Retorna un dict con los datos o None si no hay complemento.
    """
    cfdi = parse_cfdi_from_string(xml_input)
    from ..Data.cartaPorte import CartaPorteExtractor
    extractor = CartaPorteExtractor(cfdi)
    return extractor.obtener_datos_carta_porte()