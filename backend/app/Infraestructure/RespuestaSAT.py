import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple


class RespuestaSAT:

    def __init__(self, matriz_errores_path: Optional[str] = None) -> None:
        self._errores: Dict[str, str] = {}
        self._cargar_matriz(matriz_errores_path)

    # Metodo hecho por copilot (Resuelve rutas relativas y absolutas)
    def _resolver_ruta(self, path_str: str) -> Optional[str]:
        if not path_str:
            return None
        if os.path.isabs(path_str) and os.path.exists(path_str):
            return os.path.abspath(path_str)
        base = os.path.dirname(os.path.dirname(__file__))
        candidatos = [
            path_str,
            os.path.join(base, path_str),
            os.path.join(base, 'Temp', 'matriz_errores.txt'),
            os.path.join(os.path.dirname(__file__), '..', 'Temp', 'matriz_errores.txt'),
        ]
        for c in candidatos:
            c_abs = os.path.abspath(os.path.normpath(c))
            if os.path.exists(c_abs):
                return c_abs
        return None

    def _cargar_matriz(self, matriz_errores_path: Optional[str]) -> None:
        default_rel = os.path.join('Temp', 'matriz_errores.txt')
        ruta = self._resolver_ruta(matriz_errores_path or default_rel)
        if not ruta:
            return
        with open(ruta, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                codigo, mensaje = line.split('|', 1)
                self._errores[codigo.strip()] = mensaje.strip()

    def obtener_mensaje_error(self, codigo: str) -> str:
        codigo = str(codigo).strip()
        if codigo in self._errores:
            return self._errores[codigo]
        for k, v in self._errores.items():
            if codigo.startswith(k):
                return v
        # Mensaje genérico
        return f"Error del PAC/SAT (código: {codigo}). Consulte la matriz de errores."

    def procesar_respuesta(self, xml_str: str) -> Tuple[Optional[int], str]:
        if not xml_str or not xml_str.strip():
            return -3, "Respuesta vacía del PAC"
        if 'TimbreFiscalDigital' in xml_str:
            uuid = self.extraer_uuid(xml_str)
            if uuid:
                return 0, ""
            # Si no podemos parsear pero existe la cadena, lo tomamos como éxito de todos modos
            return 0, ""
        m = re.search(r'(CFDI\d{5})', xml_str)
        if m:
            cod = m.group(1)
            return -3, f"{cod}: {self.obtener_mensaje_error(cod)}"
        if re.search(r'fault|string|error|mensaje', xml_str, re.IGNORECASE):
            fragment = xml_str[:500].replace('\n', ' ').strip()
            return -3, f"Error al timbrar: {fragment}"
        return 0, ""

    def extraer_uuid(self, xml_str: str) -> Optional[str]:
        # namespaces comunes
        ns = {
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital',
        }
        root = ET.fromstring(xml_str)
        for elem in root.iter():
            if elem.tag.endswith('TimbreFiscalDigital'):
                uuid = elem.attrib.get('UUID')
                if uuid:
                    return uuid
        tfd = root.find('.//tfd:TimbreFiscalDigital', ns)
        if tfd is not None:
            return tfd.get('UUID')
        return None
    
__all__ = ["RespuestaSAT"]