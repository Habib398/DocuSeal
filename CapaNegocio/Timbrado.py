from typing import Optional, Tuple, Union
from CapaNegocio.SellarXML import SellarXML
from CapaConexion.ConfiguracionPAC import ConfiguracionPAC
from CapaConexion.PACClient import PACClientBase
from CapaNegocio.TimbradoExito import TimbradoExito
from CapaNegocio.TimbradoError import TimbradoError


class Timbrado:
    def __init__(
        self,
        idTimbrado: int,
        xmlSellador: SellarXML,
        pac_config: Optional[ConfiguracionPAC] = None,
        cliente_pac: Optional[PACClientBase] = None,
    ):
        self.idTimbrado = idTimbrado
        self.xml_sellador = xmlSellador
        self.xml_sellado: Optional[str] = xmlSellador.xmlSellado
        self.pac_config = pac_config
        self.cliente_pac = cliente_pac

    def ConectarPAC(self) -> PACClientBase:
        # Prepara/valida al cliente PAC
        if self.cliente_pac is None:
            raise RuntimeError("Cliente PAC no configurado. Proporcione una implementación de PACClientBase.")
        return self.cliente_pac

    def EnviarTimbrar(self) -> Union[TimbradoExito, TimbradoError]:
        """Envía el XML sellado al PAC y devuelve resultado estructurado."""
        # Validaciones
        if not self.xml_sellado:
            return TimbradoError(self.idTimbrado, 1001, "No se ha proporcionado XML sellado.")

        try:
            cliente = self.ConectarPAC()
            exito, xml_timbrado, codigo, mensaje = cliente.timbrar_xml(self.xml_sellado)
        except Exception as e:
            return TimbradoError(self.idTimbrado, 1002, f"Error conectando/enviando al PAC: {e}")

        if exito and xml_timbrado:
            return TimbradoExito(self.idTimbrado, xml_timbrado)
        else:
            return TimbradoError(self.idTimbrado, codigo or 1999, mensaje or "Error desconocido del PAC")

    # Utilidad para setear/actualizar el XML sellado desde el sellador
    def ActualizarDesdeSellador(self) -> None:
        self.xml_sellado = self.xml_sellador.xmlSellado