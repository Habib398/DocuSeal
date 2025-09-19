import os
from typing import Optional

from Data.ConvertirJson import ConvertirJson
from Business.ConfiguracionSello import ConfiguracionSello

from satcfdi.models import Signer
from satcfdi.cfdi import CFDI

class SellarXML:

    def _resolve_path(self, path: str) -> str:
        """Convierte una ruta relativa a absoluta, si es necesario."""
        if not os.path.isabs(path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            abs_path = os.path.join(base_dir, path)
            return abs_path
        return path
    
    def get_sello(self) -> str:
        return self.xmlSellado
    
    def __init__(self, IdSellarXML: int, complemento: ConfiguracionSello, xml: str, xmlSellado: Optional[str] = None):
        self.IdSellarXML = IdSellarXML
        self.complemento = complemento
        self.xml = xml
        self.xmlSellado = xmlSellado
        self.no_certificado_json: Optional[str] = None
        self.certificado_json: Optional[str] = None

    def _load_signer(self) -> Signer:
        cer_path = self._resolve_path(self.complemento.get_cer())
        key_path = self._resolve_path(self.complemento.get_key())
        password = self.complemento.get_pwd_cer() or None

        with open(cer_path, "rb") as f:
            cer_bytes = f.read()
        with open(key_path, "rb") as f:
            key_bytes = f.read()

        signer = Signer.load(certificate=cer_bytes, key=key_bytes, password=password)
        return signer
    
    def GenerarSello(self, xml_convertidor: Optional[ConvertirJson] = None) -> str:
        if xml_convertidor is not None:
            self.xml = xml_convertidor.GenerarXmlCFDI()
            print(self.xml)
        # ====== Agregar atributo Sello="" si no existe (Hecho por Copilot) ======
        from lxml import etree
        xml_tree = etree.fromstring(self.xml.encode('utf-8'))
        if 'Sello' not in xml_tree.attrib:
            xml_tree.set('Sello', '')
        self.xml = etree.tostring(xml_tree, encoding='utf-8', xml_declaration=True).decode('utf-8')
        # ====== Fin agregar atributo Sello ======

        cfdi = CFDI.from_string(self.xml.encode('utf-8'))
        signer = self._load_signer()
        cfdi.sign(signer)

        self.xmlSellado = cfdi.xml_bytes(pretty_print=True).decode('utf-8')
        print("=== XML SELLADO ===")
        print(self.xmlSellado)
        return self.xmlSellado
