"""
ServicioSellado.py - Service Layer para operaciones de sellado de CFDI
Acepta XML en formato string (datos_xml) o estructura JSON
"""

import logging
from typing import Dict, Any
from .SellarXML import SellarXML

logger = logging.getLogger(__name__)


class ServicioSellado:
    """
    Servicio para operaciones de sellado de CFDI desde XML o estructura JSON.
    """
    
    @staticmethod
    def sellar(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sella un CFDI recibido como XML en el campo datos_xml o como estructura JSON.
        """
        logger.info("Iniciando proceso de sellado")
        
        xml_input = data.get('datos_xml')
        if not xml_input:
            return {"error": "Falta campo 'datos_xml' en el cuerpo de la petición"}
        
        if isinstance(xml_input, str):
            logger.info(f"Sellando XML string (longitud: {len(xml_input)} caracteres)")
        else:
            logger.info("Sellando desde estructura JSON")
        
        # Sellar usando SellarXML (que ahora maneja ambos formatos)
        return SellarXML.sellar_cfdi(data)
