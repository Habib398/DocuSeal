from abc import ABC, abstractmethod
from typing import Optional
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from CapaConexion.RespuestaSAT import RespuestaSAT


class ITimbradoService(ABC):
    @abstractmethod
    def timbrar(self, xml_str: str, svc_user: str, svc_pwd: str, pruebas: bool = True) -> dict:
        pass

class TimbradoService(ITimbradoService):
    def __init__(self, matriz_errores_path: Optional[str] = None, timeout_s: int = 30) -> None:
        self.respuesta_sat = RespuestaSAT(matriz_errores_path)
        self.timeout_s = timeout_s

    def _normalizar_xml(self, xml_str: str) -> str:
        # Metodo hecho por Copilot
        # Asegura que el documento inicie exactamente con la declaración XML 1.0 UTF-8.
        if not xml_str:
            return xml_str
        # Eliminar BOM si existe
        if xml_str.startswith('\ufeff'):
            xml_str = xml_str.lstrip('\ufeff')
        # Trim left de espacios y saltos antes de la declaración
        xml_str = xml_str.lstrip('\r\n \t')
        # Detectar declaración existente
        import re as _re
        pattern = r'^<\?xml[^>]*\?>'
        if _re.match(pattern, xml_str[:80]):
            xml_str = _re.sub(pattern, '<?xml version="1.0" encoding="UTF-8"?>', xml_str, count=1)
        else:
            xml_str = '<?xml version="1.0" encoding="UTF-8"?>' + ('\n' if not xml_str.startswith('<') else '') + xml_str
        return xml_str

    def _validar_xml_sellado(self, xml_str: str) -> Optional[str]:
        # Validaciones básicas antes de enviar a timbrar (hecho por Copilot)
        try:
            root = ET.fromstring(xml_str)
        except Exception as e:
            return f"XML inválido: {e}"

        sello = root.attrib.get("Sello")
        if not sello:
            return "El XML no contiene el atributo 'Sello'. Debe sellarse antes de timbrar."
        if len(sello.strip()) < 20:
            return "El atributo 'Sello' parece incompleto. Verifique el proceso de sellado."
        return None

    def timbrar(self, xml_str: str, svc_user: str, svc_pwd: str, pruebas: bool = True) -> dict:
        # Llamar a validación de xml
        err = self._validar_xml_sellado(xml_str)
        if err:
            return {"codigo": -2, "mensaje": err, "cuerpo": "", "uuid": None}

        xml_str = self._normalizar_xml(xml_str)

        url = (
            "https://pruebas.comercio-digital.mx/timbre4/timbrarv5"
            if pruebas
            else "https://ws.comercio-digital.mx/timbre4/timbrarv5"
        )
        print(f"Enviando petición a URL: {url}")

        headers = {
            "Expect": "",
            "Content-Type": "text/xml",
            "usrws": svc_user,
            "pwdws": svc_pwd,
            "tipo": "XML",
        }

        req = urllib.request.Request(url, data=xml_str.encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                resp_headers = resp.headers
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode("utf-8", errors="replace")
            except Exception:
                err_body = ""
            return {"codigo": -1, "mensaje": f"HTTP {e.code}: {e.reason}", "cuerpo": err_body, "uuid": None}
        except urllib.error.URLError as e:
            return {"codigo": -1, "mensaje": f"Error de conexión: {e.reason}", "cuerpo": "", "uuid": None}
        except Exception as e:
            return {"codigo": -1, "mensaje": f"Error al conectar: {e}", "cuerpo": "", "uuid": None}

        codigo_header = resp_headers.get("codigo", "0")
        try:
            codigo_int = int(str(codigo_header).split("|")[0].strip())
        except Exception:
            codigo_int = 0

        if codigo_int != 0:
            # Incluir el cuerpo y headers de la respuesta del PAC
            descripcion_error = self.respuesta_sat.obtener_mensaje_error(str(codigo_int))
            header_errmsg = (
                resp_headers.get("errmsg")
                or resp_headers.get("errormsg")
                or resp_headers.get("error")
            )
            mensaje_detallado = header_errmsg or descripcion_error
            return {
                "codigo": codigo_int,
                "mensaje": descripcion_error if not header_errmsg else descripcion_error,
                "errmsg": mensaje_detallado,
                "cuerpo": body,
                "uuid": None,
                "headers": {k: v for k, v in resp_headers.items()}
            }

        # Procesar respuesta XML para detectar códigos internos y extraer UUID
        codigo_xml, descripcion_xml = self.respuesta_sat.procesar_respuesta(body)
        uuid = self.respuesta_sat.extraer_uuid(body)

        codigo_final = codigo_int if not codigo_xml else codigo_xml
        mensaje_final = descripcion_xml if codigo_xml else ""

        return {"codigo": codigo_final, "mensaje": mensaje_final, "errmsg": mensaje_final, "cuerpo": body, "uuid": uuid}

timbrado_service = TimbradoService()