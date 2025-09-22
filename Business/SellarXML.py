import os
from typing import Optional
from DB.DBManager import DBManager
from Data.ConvertirJson import ConvertirJson
from Business.ConfiguracionSello import ConfiguracionSello
import base64
import tempfile
from satcfdi.models import Signer
from satcfdi.cfdi import CFDI

class SellarXML:
    
    def __init__(self, IdSellarXML: int, complemento: ConfiguracionSello, xml: str, xmlSellado: Optional[str] = None):
        self.IdSellarXML = IdSellarXML
        self.complemento = complemento
        self.xml = xml
        self.xmlSellado = xmlSellado
        self.no_certificado_json: Optional[str] = None
        self.certificado_json: Optional[str] = None

    def _resolve_path(self, path: str) -> str:
        # Convierte una ruta relativa a absoluta, si es necesario. (Hecho por Copilot)
        if not os.path.isabs(path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            abs_path = os.path.join(base_dir, path)
            return abs_path
        return path
    
    def get_sello(self) -> str:
        return self.xmlSellado

    def obtener_cer_db(self, noCertificado: str) -> Optional[str]:
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        print(f"[LOG] Resultado consulta CER para noCertificado={noCertificado}: {registro}")
        if registro:
            print(f"[LOG] CER obtenido: {registro[3]}")
            return registro[3]  # CER está en la posición 3
        print("[LOG] No se encontró registro para CER")
        return None

    def obtener_key_db(self, noCertificado: str) -> Optional[str]:
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        print(f"[LOG] Resultado consulta KEY para noCertificado={noCertificado}: {registro}")
        if registro:
            print(f"[LOG] KEY obtenido: {registro[4]}")
            return registro[4]  # KEY está en la posición 4
        print("[LOG] No se encontró registro para KEY")
        return None

    def convertir_cer(self, cer_b64: str) -> bytes:
        return base64.b64decode(cer_b64)
    
    def convertir_key(self, key_b64: str) -> bytes:
        return base64.b64decode(key_b64)
    
    def archivar_cer(self, cer_b64: str, filename: str) -> str:
        cer_bytes = self.convertir_cer(cer_b64)
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".cer")
        tmpfile.write(cer_bytes)
        tmpfile.close()
        return tmpfile.name
    
    def archivar_key(self, key_b64: str, filename: str) -> str:
        key_bytes = self.convertir_key(key_b64)
        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".key")
        tmpfile.write(key_bytes)
        tmpfile.close()
        return tmpfile.name

    def _load_signer(self) -> Signer:
        cer_data = self.complemento.get_cer()
        key_data = self.complemento.get_key()
        password = self.complemento.get_pwd_cer() or None

        # Determinar si son rutas de archivos o contenido base64
        if os.path.exists(cer_data):
            # Es una ruta de archivo
            cer_path = self._resolve_path(cer_data)
            with open(cer_path, "rb") as f:
                cer_bytes = f.read()
        else:
            # Es contenido base64
            cer_bytes = base64.b64decode(cer_data)

        if os.path.exists(key_data):
            # Es una ruta de archivo
            key_path = self._resolve_path(key_data)
            with open(key_path, "rb") as f:
                key_bytes = f.read()
        else:
            # Es contenido base64
            key_bytes = base64.b64decode(key_data)

        signer = Signer.load(certificate=cer_bytes, key=key_bytes, password=password)
        return signer
    
    def limpiar_temporal(self, ruta: str) -> None:
        if os.path.exists(ruta):
            os.remove(ruta)
    
    def GenerarSello(self, xml_convertidor: Optional[ConvertirJson] = None) -> str:
        if xml_convertidor is not None:
            self.xml = xml_convertidor.GenerarXmlCFDI()

        # Agregar atributo Sello="" si no existe (Hecho por Copilot)
        from lxml import etree
        xml_tree = etree.fromstring(self.xml.encode('utf-8'))
        if 'Sello' not in xml_tree.attrib:
            xml_tree.set('Sello', '')
        self.xml = etree.tostring(xml_tree, encoding='utf-8', xml_declaration=True).decode('utf-8')

        cfdi = CFDI.from_string(self.xml.encode('utf-8'))
        signer = self._load_signer()
        cfdi.sign(signer)

        self.xmlSellado = cfdi.xml_bytes(pretty_print=True).decode('utf-8')
        return self.xmlSellado
