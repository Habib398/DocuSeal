import base64
import os
from CapaDatos.ConvertirJson import ConvertirJson
from CapaNegocio.ConfiguracionSello import ConfiguracionSello
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from typing import Optional
from CapaDatos.ConfiguracionCadenaOriginal import CadenaOriginalGenerator

class SellarXML:
    
    def __init__(self, IdSellarXML: int, complemento: ConfiguracionSello, xml: str, xmlSellado: Optional[str] = None):
        self.IdSellarXML = IdSellarXML
        self.complemento = complemento
        self.xml = xml
        self.xmlSellado = xmlSellado
        # Nuevos atributos para almacenar NoCertificado y Certificado provenientes del JSON
        self.no_certificado_json: Optional[str] = None
        self.certificado_json: Optional[str] = None

    def _resolve_path(self, path_str: str) -> str:
        """Resuelve rutas relativas probando ubicaciones comunes dentro del proyecto."""
        if not path_str:
            raise FileNotFoundError("Ruta vacía proporcionada")
        if os.path.isabs(path_str) and os.path.exists(path_str):
            return os.path.abspath(path_str)
        base_dirs = [
            os.getcwd(),
            os.path.dirname(__file__),
            os.path.join(os.path.dirname(__file__), '..'),
            os.path.dirname(os.path.dirname(__file__)),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Temp'),
        ]
        candidates = [path_str] + [os.path.join(b, path_str) for b in base_dirs]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        raise FileNotFoundError(f"Archivo no encontrado ('{path_str}'). Rutas intentadas: {candidates}")

    def cargarLlavePrivada(self):
        key_str = self.complemento.get_key()
        pwd = self.complemento.get_pwd_cer()
        key_path = self._resolve_path(key_str)
        with open(key_path, "rb") as key_file:
            key_data = key_file.read()
        private_key = serialization.load_der_private_key(
            key_data,
            password=pwd.encode() if pwd else None,
        )
        return private_key

    def cargarCertificado(self):
        cert_str = self.complemento.get_cer()
        cert_path = self._resolve_path(cert_str)
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()
        cert = x509.load_der_x509_certificate(cert_data)
        return cert

    def generarCadenaOriginal(self, xmlStr: ConvertirJson) -> str:
        # Generar cadena original a partir del XML
        origen = self.xml if isinstance(self.xml, str) else xmlStr
        return CadenaOriginalGenerator.generar(origen)
    
    def GenerarSello(self, cadena_original: str) -> str:
        private_key = self.cargarLlavePrivada()
        #  calcular hashes
        signature = private_key.sign(
            cadena_original.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        #  codificar en base64
        sello_base64 = base64.b64encode(signature).decode("utf-8")
        return sello_base64

    def agregarSelloAlXML(self, sello: str) -> str:
        # Metodo hecho por Copilot
        # Usar lxml para preservar prefijos de namespace (evitar ns0)
        from lxml import etree as LET
        parser = LET.XMLParser(remove_blank_text=True, resolve_entities=False, no_network=True, load_dtd=False)
        root = LET.fromstring(self.xml.encode("utf-8"), parser=parser)
        # Agregar atributos Sello, NoCertificado y Certificado al elemento Comprobante
        root.set("Sello", sello)
        
        if self.no_certificado_json and not root.get("NoCertificado"):
            root.set("NoCertificado", self.no_certificado_json)
        if self.certificado_json and not root.get("Certificado"):
            root.set("Certificado", self.certificado_json)

        # Serializar conservando los prefijos declarados en nsmap (cfdi/xsi), sin "ns0"
        xml_con_sello = LET.tostring(
            root,
            encoding="utf-8",
            xml_declaration=True,
            pretty_print=False,
        ).decode("utf-8")
        print(xml_con_sello)
        # Verificar que el XML está en UTF-8 sin BOM
        xml_bytes = xml_con_sello.encode("utf-8")
        # BOM en UTF-8 es b'\xef\xbb\xbf'
        if xml_bytes.startswith(b'\xef\xbb\xbf'):
            print("ADVERTENCIA: El XML tiene BOM. Esto puede causar error 301 en el PAC.")
        else:
            print("El XML está en UTF-8 sin BOM.")
        return xml_con_sello

    def sellar_y_completar(self, xml_convertidor: Optional[ConvertirJson] = None) -> str:
        # Insertar el sello y completar el XML con NoCertificado y Certificado
        if xml_convertidor is not None:
            self.xml = xml_convertidor.GenerarXmlCFDI()
            datos = xml_convertidor.datos_xml.get("cfdi:Comprobante", {})
            no_cert = datos.get("NoCertificado") or datos.get("noCertificado")
            cert = datos.get("Certificado") or datos.get("certificado")
            if no_cert:
                self.no_certificado_json = str(no_cert)
            if cert:
                self.certificado_json = str(cert)
        cadena = self.generarCadenaOriginal(xml_convertidor if xml_convertidor else None)
        sello = self.GenerarSello(cadena)
        self.xmlSellado = self.agregarSelloAlXML(sello)
        return self.xmlSellado

    # Getters de soporte para acceso externo
    def get_no_certificado_json(self) -> Optional[str]:
        return self.no_certificado_json

    def get_certificado_json(self) -> Optional[str]:
        return self.certificado_json
