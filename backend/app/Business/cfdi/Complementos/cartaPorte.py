from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict, Any
from satcfdi.cfdi import CFDI
from satcfdi.create.cfd.cartaporte31 import CartaPorte


class CartaPorteExtractor:
    def __init__(self, cfdi: CFDI):
        self.cfdi = cfdi

    def extraer_carta_porte(self) -> Optional[CartaPorte]:
        """
        Extrae el complemento CartaPorte del CFDI si existe.
        Retorna el objeto CartaPorte o None si no hay complemento.
        """
        complemento = self.cfdi.get('Complemento')
        if not complemento:
            return None
        
        carta_porte_data = complemento.get('CartaPorte')
        if not carta_porte_data:
            return None
        
        # objeto carta porte
        if isinstance(carta_porte_data, CartaPorte):
            return carta_porte_data
        return None

    def obtener_datos_carta_porte(self) -> Optional[Dict[str, Any]]:
        """
        Retorna los datos del complemento CartaPorte como un dict para facilitar el acceso.
        """
        carta_porte = self.extraer_carta_porte()
        if not carta_porte:
            return None
        
        # Acceder a atributos del objeto CartaPorte
        return {
            'version': getattr(carta_porte, 'version', None),
            'id_ccp': getattr(carta_porte, 'id_ccp', None),
            'transp_internac': getattr(carta_porte, 'transp_internac', None),
            'total_dist_rec': getattr(carta_porte, 'total_dist_rec', None),
            'ubicaciones': getattr(carta_porte, 'ubicaciones', []),
            'mercancias': getattr(carta_porte, 'mercancias', None)
        }