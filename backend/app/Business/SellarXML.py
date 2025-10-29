"""
SellarXML.py - Clase para el sellado de CFDI
Maneja el sellado criptográfico de documentos CFDI usando certificados de la base de datos.
"""

from asyncio.log import logger
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
    def obtener_datos_certificado_por_clave(claveUsuario: str) -> Optional[dict]:
        """
        Obtiene todos los datos del certificado usando claveUsuario.
        """
        from .Configuration.ConfiguracionCertificados import ConfiguracionCertificados
        
        db = DBManager()
        config_cert = ConfiguracionCertificados(db)
        certificado = config_cert.obtener_por_clave_usuario(claveUsuario)
        
        if not certificado:
            return None
        
        # Decodificar CER y KEY de base64 a bytes
        cer_b64 = certificado.get('CER')
        key_b64 = certificado.get('KEY')
        
        try:
            cer_bytes = base64.b64decode(cer_b64) if cer_b64 else None
            key_bytes = base64.b64decode(key_b64) if key_b64 else None
        except Exception as e:
            raise ValueError(f"Error decodificando CER/KEY: {str(e)}")
        
        return {
            'cer_bytes': cer_bytes,
            'key_bytes': key_bytes,
            'certificado_texto': certificado.get('Certificado'),
            'pwd_cer': certificado.get('pwdCER', ''),
            'no_certificado': certificado.get('noCertificado')
        }

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
        Requiere claveUsuario para obtener los certificados de la BD.
        Acepta:
        - "xml": string XML
        - "datosXML": estructura JSON (dict)
        - "claveUsuario": clave única del certificado
        """
        try:
            # Validar que venga claveUsuario
            clave_usuario = data.get("claveUsuario")
            if not clave_usuario:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML001",
                        "mensaje": "Falta el campo 'claveUsuario' en la petición"
                    }]
                }
            
            # Verificar qué formato viene
            xml_string_input = data.get("xml")
            json_input = data.get("datosXML")
            
            # CASO 1: Viene como estructura JSON en "datosXML"
            if json_input and isinstance(json_input, dict):
                
                # Convertir JSON a XML usando ConvertirJson
                from .cfdi.ConvertirJson import ConvertirJson
                try:
                    converter = ConvertirJson(json_input)
                    xml_input = converter.GenerarXmlCFDI()
                except Exception as e:
                    return {
                        "errores": [{
                            "tipo": "error",
                            "codigo": "SXML002",
                            "mensaje": f"Error al convertir JSON a XML: {str(e)}"
                        }]
                    }
            
            # CASO 2: Viene como XML string en "xml"
            elif xml_string_input and isinstance(xml_string_input, str):
                xml_input = xml_string_input.strip()
            
            # CASO 3: No viene ninguno de los dos formatos válidos
            else:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML003",
                        "mensaje": "Debe proporcionar 'xml' (string XML) o 'datosXML' (estructura JSON)"
                    }]
                }
            
            # Limpiar y normalizar el XML (eliminar espacios/saltos de línea innecesarios)
            import re
            xml_input = re.sub(r'>\s+<', '><', xml_input)
            
            # Obtener datos del certificado usando claveUsuario
            datos_cert = cls.obtener_datos_certificado_por_clave(clave_usuario)
            if not datos_cert:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML004",
                        "mensaje": f"No se encontró certificado con claveUsuario: {clave_usuario}"
                    }]
                }
            
            cer_bytes = datos_cert['cer_bytes']
            key_bytes = datos_cert['key_bytes']
            certificado_texto = datos_cert['certificado_texto']
            pwd_cer = datos_cert['pwd_cer']
            no_certificado = datos_cert['no_certificado']
            
            if not cer_bytes or not key_bytes:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML005",
                        "mensaje": "No se encontraron CER o KEY en la base de datos para el certificado proporcionado."
                    }]
                }
            
            if not certificado_texto:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML006",
                        "mensaje": "No se encontró el campo Certificado en la base de datos para el certificado proporcionado."
                    }]
                }
            
            if not no_certificado:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML007",
                        "mensaje": "No se encontró el noCertificado en la base de datos."
                    }]
                }
            
            # Parsear XML y actualizar campos desde la BD
            from lxml import etree
            try:
                xml_tree = etree.fromstring(xml_input.encode('utf-8'))
            except Exception as e:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML008",
                        "mensaje": f"Error al parsear XML: {str(e)}"
                    }]
                }

            # Establecer NoCertificado y Certificado desde la base de datos
            xml_tree.set('NoCertificado', no_certificado)
            xml_tree.set('Certificado', certificado_texto)
            xml_generado = etree.tostring(xml_tree, encoding='utf-8', xml_declaration=True).decode('utf-8')

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
                "xml_con_sello": xml_con_sello
            }
                
        except Exception as e:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "SXML009",
                    "mensaje": f"Error general en el proceso de sellado: {str(e)}"
                }]
            }

    def GenerarSello(self) -> str:
        """
        Genera el sello digital del CFDI.
        """
        # Agregar atributo sello si no existe en xml
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
