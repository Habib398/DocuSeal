from CapaNegocio.ConfiguracionSello import ConfiguracionSello


class SellarXML:
    def __init__(self, IdSellarXML: int, complemento: ConfiguracionSello, xml: str, xmlSellado: str):
        self.IdSellarXML = IdSellarXML
        self.complemento = complemento.complementoStr
        self.xml = xml
        self.xmlSellado = xmlSellado

    def Sellar(self):
        # Lógica para sellar el XML
        pass
