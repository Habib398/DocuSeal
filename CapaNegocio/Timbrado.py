from CapaNegocio.SellarXML import SellarXML


class Timbrado:
    def __init__(self, idTimbrado: int, xmlSellado: SellarXML, sello: bool = False):
        self.idTimbrado = idTimbrado
        self.xmlSellado = xmlSellado.xmlSellado
        self.sello = sello

    def ConectarPAC(self):
        # Lógica para conectar con el PAC
        pass

    def EnviarTimbrar(self):
        # Lógica para enviar a timbrar
        pass