import dicttoxml
from pydantic import BaseModel

class JsonInput(BaseModel):
    data: dict

class ConvertirJson:
    def __init__(self, datos_xml: dict):
        self.datos_xml = datos_xml

    def GenerarXml(self):
        # Si no hay datos que convertir, devolver error
        if not self.datos_xml:
            return 
        
        xml_bytes = dicttoxml.dicttoxml(self.datos_xml, custom_root='CFDI', attr_type=False)
        print(xml_bytes)
        return xml_bytes.decode("utf-8")