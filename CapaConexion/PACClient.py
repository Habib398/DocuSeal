from typing import Optional, Tuple

from CapaConexion.ConfiguracionPAC import ConfiguracionPAC


class PACClientBase:
    """Interfaz base para clientes PAC.
    Implementaciones reales deben sobrescribir timbrar_xml.
    """

    def __init__(self, config: ConfiguracionPAC):
        self.config = config

    def timbrar_xml(self, xml_sellado: str) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
        #Envía el XML sellado al PAC y regresa: error, xml_timbrado, codigo_error, mensaje_error
        raise NotImplementedError


__all__ = ["PACClientBase", "ConfiguracionPAC"]
