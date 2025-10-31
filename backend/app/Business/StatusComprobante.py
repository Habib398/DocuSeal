from satcfdi.cfdi import CFDI
from satcfdi.pacs.sat import SAT
import re

def Verificar_status_cfdi(xml: str) -> dict:
    # Limpiar XML eliminando declaración de encoding UTF-8
    xml = re.sub(r"<\?xml[^>]*encoding=['\"]?utf-8['\"]?[^>]*\?>", "", xml, flags=re.IGNORECASE)
    xml = xml.strip()

    sat = SAT()
    res = sat.status(
        cfdi=CFDI.from_string(xml)
    )
    return res