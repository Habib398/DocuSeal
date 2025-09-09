import base64
import os
from CapaDatos.ConvertirJson import ConvertirJson
from CapaNegocio.ConfiguracionSello import ConfiguracionSello
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from cryptography.x509.oid import NameOID
import xml.etree.ElementTree as ET
from typing import Optional
from lxml import etree

class SellarXML:
    """CER y KEY, como los recibo y cargo?, direccion o ruta de los archivos?,
    si el cliente pone la ruta de su archivo igual funciona?"""
    
    def __init__(self, IdSellarXML: int, complemento: ConfiguracionSello, xml: str, xmlSellado: Optional[str] = None):
        self.IdSellarXML = IdSellarXML
        self.complemento = complemento
        self.xml = xml
        self.xmlSellado = xmlSellado

    def _resolve_path(self, path_str: str) -> str:
        """Resuelve rutas relativas probando ubicaciones comunes dentro del proyecto."""
        if not path_str:
            raise FileNotFoundError("Ruta vacía proporcionada")
        # Si es absoluta y existe
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
            try:
                if os.path.exists(c):
                    return os.path.abspath(c)
            except Exception:
                continue
        raise FileNotFoundError(f"Archivo no encontrado ('{path_str}'). Rutas intentadas: {candidates}")

    def cargarLlavePrivada(self):
        key_str = self.complemento.get_key()
        pwd = self.complemento.get_pwd_cer()

        key_path = self._resolve_path(key_str)
        with open(key_path, "rb") as key_file:
            key_data = key_file.read()

        try:
            # Detectar si es PEM (texto) o DER (binario)
            if key_data.strip().startswith(b"-----BEGIN"):
                private_key = serialization.load_pem_private_key(
                    key_data,
                    password=pwd.encode() if pwd else None,
                )
            else:
                private_key = serialization.load_der_private_key(
                    key_data,
                    password=pwd.encode() if pwd else None,
                )
        except Exception as e:
            raise RuntimeError(f"Error cargando llave privada '{key_str}': {e}")
        return private_key

    def cargarCertificado(self):
        cert_str = self.complemento.get_cer()
        cert_path = self._resolve_path(cert_str)
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()

        try:
            if cert_data.strip().startswith(b"-----BEGIN"):
                cert = x509.load_pem_x509_certificate(cert_data)
            else:
                cert = x509.load_der_x509_certificate(cert_data)
        except Exception as e:
            raise RuntimeError(f"Error cargando certificado '{cert_str}': {e}")

        return cert

    def generarCadenaOriginal(self, xmlStr: ConvertirJson) -> str:
        # Genera la cadena original a partir del XML generado y el XSLT del SAT.

        xmlString = self.xml if isinstance(self.xml, str) else xmlStr.GenerarXmlCFDI()

        # Resolver ruta del XSLT de forma robusta
        xslt_rel = os.path.join(os.path.dirname(__file__), '..', 'CapaDatos', 'cadenaoriginal_4_0.xslt')
        xslt_path = os.path.abspath(os.path.normpath(xslt_rel))
        if not os.path.exists(xslt_path):
            raise FileNotFoundError(f"XSLT no encontrado: {xslt_path}")

        # Parsers seguros
        xslt_parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
        xml_parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, no_network=True, load_dtd=False)

        # Cargar y compilar XSLT
        with open(xslt_path, 'rb') as f:
            xslt_doc = etree.parse(f, parser=xslt_parser)
        transform = etree.XSLT(xslt_doc)

        # Parsear el XML generado
        xml_doc = etree.fromstring(xmlString.encode('utf-8'), parser=xml_parser)
        # Transformar el XML usando el XSLT
        result_tree = transform(xml_doc)
        cadena_original = str(result_tree)
        return cadena_original
    
    def GenerarSello(self, cadena_original: str) -> str:
        private_key = self.cargarLlavePrivada()
        # Firmar cadena original
        signature = private_key.sign(
            cadena_original.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        sello_base64 = base64.b64encode(signature).decode("utf-8")
        return sello_base64
    
    def _obtener_no_certificado(self, cert: x509.Certificate) -> str:
        # Extrae el NoCertificado
        try:
            attrs = cert.subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
            if attrs:
                # Quitar espacios por si el proveedor los incluye
                return attrs[0].value.replace(" ", "")
        except Exception:
            pass
        # Fallback: usar el entero del serial (puede no coincidir con el formato SAT)
        try:
            return str(cert.serial_number)
        except Exception:
            return ""

    def _obtener_certificado_b64(self, cert: x509.Certificate) -> str:
        der_bytes = cert.public_bytes(serialization.Encoding.DER)
        return base64.b64encode(der_bytes).decode("utf-8")

    def agregarSelloAlXML(self, sello: str) -> str:
        root = ET.fromstring(self.xml)
        # Agregar atributos Sello, NoCertificado y Certificado al elemento Comprobante
        root.set("Sello", sello)

        # Cargar certificado para obtener NoCertificado y Certificado
        cert = self.cargarCertificado()
        no_cert = self._obtener_no_certificado(cert)
        cert_b64 = self._obtener_certificado_b64(cert)

        if no_cert:
            root.set("NoCertificado", no_cert)
        if cert_b64:
            root.set("Certificado", cert_b64)
        # Convertir de nuevo a string
        xml_con_sello = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
        print(xml_con_sello)
        return xml_con_sello

    def sellar_y_completar(self, xml_convertidor: Optional[ConvertirJson] = None) -> str:
        """Orquesta el proceso: genera cadena original, firma, e inserta atributos.

        - Usa self.xml si ya viene el XML generado.
        - Si se proporciona xml_convertidor, se puede usar para regenerar el XML antes de sellar.
        Devuelve el XML sellado con Sello, NoCertificado y Certificado.
        """
        if xml_convertidor is not None:
            # Regenerar XML si se proporcionó convertidor
            self.xml = xml_convertidor.GenerarXmlCFDI()

        cadena = self.generarCadenaOriginal(xml_convertidor if xml_convertidor else None)
        sello = self.GenerarSello(cadena)
        self.xmlSellado = self.agregarSelloAlXML(sello)
        return self.xmlSellado
