"""
SellarXML.py - Clase para el sellado de CFDI
Maneja el sellado criptográfico de documentos CFDI usando certificados de la base de datos.
"""

from typing import Optional
from DB.DBManager import DBManager
import base64
from satcfdi.models import Signer
from satcfdi.cfdi import CFDI


class SellarXML:
    """
    Clase para el sellado de documentos CFDI.
    Obtiene los certificados CER y KEY desde la base de datos y realiza el sellado digital.
    """

    def __init__(self, id: int, xml: str, cer_bytes: bytes, key_bytes: bytes, password: Optional[str] = None, xmlSellado: Optional[str] = None):
        self.id = id
        self.xml = xml
        self.cer_bytes = cer_bytes
        self.key_bytes = key_bytes
        self.password = password
        self.xmlSellado = xmlSellado
        self.cadena_original: Optional[str] = None

    def get_sello(self) -> str:
        """Retorna el XML sellado"""
        return self.xmlSellado
    
    def get_cadena_original(self) -> Optional[str]:
        """Retorna la cadena original generada durante el sellado"""
        return self.cadena_original

    @staticmethod
    def obtener_cer_db(noCertificado: str) -> Optional[bytes]:
        """
        Obtiene el campo CER de la base de datos en formato bytes.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            cer_b64 = registro.get('CER')
            if cer_b64:
                try:
                    return base64.b64decode(cer_b64)
                except Exception as e:
                    raise ValueError(f"Error decodificando CER: {str(e)}")
        return None

    @staticmethod
    def obtener_key_db(noCertificado: str) -> Optional[bytes]:
        """
        Obtiene el campo KEY de la base de datos en formato bytes.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            key_b64 = registro.get('KEY')
            if key_b64:
                try:
                    return base64.b64decode(key_b64)
                except Exception as e:
                    raise ValueError(f"Error decodificando KEY: {str(e)}")
        return None

    @staticmethod
    def obtener_certificado_db(noCertificado: str) -> Optional[str]:
        """
        Obtiene el campo Certificado (texto base64) de la base de datos.
        Este campo contiene el certificado en formato base64 tal como se usa en el XML.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            return registro.get('Certificado')
        return None

    @staticmethod
    def obtener_password_db(noCertificado: str) -> str:
        """
        Obtiene la contraseña del certificado desde la base de datos.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            pwd = registro.get('pwdCER')
            return pwd if pwd else ''
        return ''
    
    def _load_signer(self) -> Signer:
        """
        Carga el signer (firmador) usando los certificados en bytes.
        """
        return Signer.load(
            certificate=self.cer_bytes, 
            key=self.key_bytes, 
            password=self.password
        )
    
    @classmethod
    def sellar_cfdi(cls, data: dict) -> dict:
        """
        Método principal para sellar un CFDI.
        Acepta datos_xml como string (XML).
        """
        try:
            # Obtener NoCertificado del XML
            if "datos_xml" not in data or not isinstance(data["datos_xml"], str):
                return {"error": "El campo 'datos_xml' debe ser un string XML"}
            
            from lxml import etree
            try:
                xml_tree = etree.fromstring(data["datos_xml"].encode('utf-8'))
                no_certificado = xml_tree.get('NoCertificado')
            except Exception as e:
                return {"error": f"Error al parsear XML en datos_xml: {str(e)}"}
            
            if not no_certificado:
                return {"error": "Falta el campo 'NoCertificado' en el XML"}

            # Obtener CER, KEY, Certificado y contraseña de la base de datos
            cer_bytes = cls.obtener_cer_db(no_certificado)
            key_bytes = cls.obtener_key_db(no_certificado)
            certificado_texto = cls.obtener_certificado_db(no_certificado)
            pwd_cer_db = cls.obtener_password_db(no_certificado)
            
            if not cer_bytes or not key_bytes:
                return {"error": "No se encontraron CER o KEY en la base de datos para el noCertificado proporcionado."}
            
            if not certificado_texto:
                return {"error": "No se encontró el campo Certificado en la base de datos para el noCertificado proporcionado."}

            # Establecer el campo Certificado desde la base de datos (sobrescribir si existe)
            xml_tree.set('Certificado', certificado_texto)
            xml_generado = etree.tostring(xml_tree, encoding='utf-8', xml_declaration=True).decode('utf-8')

            # Obtener password del certificado desde la base de datos
            pwd_cer = pwd_cer_db if pwd_cer_db else None

            # Crear sellador con los bytes obtenidos de la BD
            sellador = cls(
                id=1,
                xml=xml_generado,
                cer_bytes=cer_bytes,
                key_bytes=key_bytes,
                password=pwd_cer
            )
            
            # Generar sello
            xml_con_sello = sellador.GenerarSello()
            
            return {
                "xml_con_sello": xml_con_sello,
                "cadena_original": sellador.cadena_original
            }
                
        except Exception as e:
            return {"error": f"Error general en el proceso de sellado: {str(e)}"}

    def GenerarSello(self) -> str:
        """
        Genera el sello digital del CFDI.
        """
        # Agregar atributo Sello="" si no existe
        from lxml import etree
        xml_tree = etree.fromstring(self.xml.encode('utf-8'))
        if 'Sello' not in xml_tree.attrib:
            xml_tree.set('Sello', '')
        self.xml = etree.tostring(xml_tree, encoding='utf-8', xml_declaration=True).decode('utf-8')

        # Crear CFDI y firmar
        cfdi = CFDI.from_string(self.xml.encode('utf-8'))
        signer = self._load_signer()
        cfdi.sign(signer)

        # Guardar la cadena original generada
        self.cadena_original = cfdi.cadena_original()

        # Generar XML sellado
        self.xmlSellado = cfdi.xml_bytes(pretty_print=True).decode('utf-8')
        return self.xmlSellado
