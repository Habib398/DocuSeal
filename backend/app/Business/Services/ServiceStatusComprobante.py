"""
ServiceStatusComprobante.py - Service Layer para verificar estatus de CFDI
"""

import logging
from typing import Dict, Any
import xml.etree.ElementTree as ET
from Business.StatusComprobante import Verificar_status_cfdi

logger = logging.getLogger(__name__)

class ServiceStatusComprobante:
    """
    Servicio para verificar el estatus de un CFDI timbrado.
    """
    
    @staticmethod
    def verificar_estatus(data: Dict[str, Any]) -> Dict[str, Any]:   
        # Extraer XML
        xml_input = data.get('xml_timbrado')

        if not xml_input:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "STAT001",
                    "mensaje": "Falta campo 'xml_timbrado' en el cuerpo de la petición"
                }]
            }
        
        # Verificar si el XML está timbrado
        if not ServiceStatusComprobante.Verificar_timbrado(xml_input):
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "STAT003",
                    "mensaje": "El XML proporcionado no está timbrado. No se puede verificar el estatus."
                }]
            }
        
        try:
            resultado = Verificar_status_cfdi(xml_input)
            return resultado
            
        except Exception as e:
            logger.exception("Error al verificar estatus del CFDI")
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "STAT002",
                    "mensaje": f"Error interno al verificar estatus: {str(e)}"
                }]
            }
    
    @staticmethod
    def Verificar_timbrado(xml_string: str) -> bool:
        """
        Verifica si el XML contiene el complemento de timbre fiscal digital.
        """
        try:
            root = ET.fromstring(xml_string)
            
            # Buscar el namespace del timbre fiscal digital
            ns = {'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
            
            # Verificar si existe el elemento TimbreFiscalDigital
            timbre = root.find('.//tfd:TimbreFiscalDigital', ns)
            
            if timbre is not None:
                # Verificar que tenga UUID
                uuid = timbre.get('UUID')
                if uuid:
                    return True
            
            return False
            
        except Exception as e:
            return False
