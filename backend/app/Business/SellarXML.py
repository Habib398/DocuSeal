import os
from typing import Optional
from DB.DBManager import DBManager
from Data.ConvertirJson import ConvertirJson
from Business.ConfiguracionSello import ConfiguracionSello
import base64
import tempfile
import json
from satcfdi.models import Signer
from satcfdi.cfdi import CFDI
from cryptography.fernet import Fernet

class SellarXML:

    def __init__(self,id: int, complemento: ConfiguracionSello, xml: str, xmlSellado: Optional[str] = None):
        self.id = id
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
            # Compatibilidad con dict (PostgreSQL) y tuple/list (SQLite legacy)
            if isinstance(registro, dict):
                cer_value = registro.get('cer')
                print(f"[LOG] CER obtenido (dict): {cer_value}")
                return cer_value
            elif isinstance(registro, (list, tuple)):
                print(f"[LOG] CER obtenido (tuple): {registro[3]}")
                return registro[3]  # CER está en la posición 3
        print("[LOG] No se encontró registro para CER")
        return None

    def obtener_key_db(self, noCertificado: str) -> Optional[str]:
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        print(f"[LOG] Resultado consulta KEY para noCertificado={noCertificado}: {registro}")
        if registro:
            # Compatibilidad con dict (PostgreSQL) y tuple/list (SQLite legacy)
            if isinstance(registro, dict):
                key_value = registro.get('key')
                print(f"[LOG] KEY obtenido (dict): {key_value}")
                return key_value
            elif isinstance(registro, (list, tuple)):
                print(f"[LOG] KEY obtenido (tuple): {registro[4]}")
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

        if os.path.exists(cer_data):
            # Ruta de archivo
            cer_path = self._resolve_path(cer_data)
            with open(cer_path, "rb") as f:
                cer_bytes = f.read()
        else:
            # Contenido base64
            cer_bytes = base64.b64decode(cer_data)

        if os.path.exists(key_data):
            # Ruta de archivo
            key_path = self._resolve_path(key_data)
            with open(key_path, "rb") as f:
                key_bytes = f.read()
        else:
            # Contenido base64
            key_bytes = base64.b64decode(key_data)

        signer = Signer.load(certificate=cer_bytes, key=key_bytes, password=password)
        return signer
    
    def limpiar_temporal(self, ruta: str) -> None:
        if os.path.exists(ruta):
            os.remove(ruta)
    
    @classmethod
    def sellar_cfdi(cls, data: dict) -> dict:
        try:
            # Obtener NoCertificado del JSON
            no_certificado = None
            if "datos_xml" in data and isinstance(data["datos_xml"], dict):
                comprobante = data["datos_xml"].get("cfdi:Comprobante")
                if comprobante and isinstance(comprobante, dict):
                    no_certificado = comprobante.get("NoCertificado")
            
            if not no_certificado:
                return {"error": "Falta el campo 'NoCertificado' en 'datos_xml.cfdi:Comprobante'"}

            # Obtener CER y KEY
            sellador_temp = cls(1, None, None)
            cer_b64 = sellador_temp.obtener_cer_db(no_certificado)
            key_b64 = sellador_temp.obtener_key_db(no_certificado)
            
            if not cer_b64 or not key_b64:
                return {"error": "No se encontraron CER o KEY en la base de datos para el noCertificado proporcionado."}

            # Generar XML
            convertir = ConvertirJson(data["datos_xml"])
            xml_generado = convertir.GenerarXmlCFDI()

            # Obtener pwdCER de JSON
            pwd_cer = ""
            if "certificado" in data and isinstance(data["certificado"], dict):
                pwd_cer = data["certificado"].get("pwdCER", "")

            # Crear archivos temporales de CER y KEY
            cer_path = sellador_temp.archivar_cer(cer_b64, "temp_cert.cer")
            key_path = sellador_temp.archivar_key(key_b64, "temp_key.key")

            # Crear configuración con rutas de archivos temporales
            certificado_json = {
                "CER": cer_path,
                "KEY": key_path,
                "pwdCER": pwd_cer
            }
            raw_body = json.dumps({"certificado": certificado_json})
            fernet_key = Fernet.generate_key().decode()
            configuracion = ConfiguracionSello(raw_body, fernet_key.encode())

            # Crear sellador y generar sello
            sellador = cls(1, configuracion, xml_generado)
            
            try:
                xml_con_sello = sellador.GenerarSello(convertir)
                # Eliminar archivos temporales
                sellador.limpiar_temporal(cer_path)
                sellador.limpiar_temporal(key_path)
                return {"xml_con_sello": xml_con_sello}
            except Exception as e:
                # Eliminar archivos temporales en caso de error
                sellador.limpiar_temporal(cer_path)
                sellador.limpiar_temporal(key_path)
                return {"error": str(e)}
                
        except Exception as e:
            return {"error": f"Error general en el proceso de sellado: {str(e)}"}

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