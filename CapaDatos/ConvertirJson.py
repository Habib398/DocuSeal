import dicttoxml
from pydantic import BaseModel

class JsonInput(BaseModel):
    data: dict

class ConvertirJson:
    def __init__(self, data: dict):
        self.data = data

    def GenerarXml(self):
        xml = dicttoxml.dicttoxml(self.data, custom_root='root', attr_type=False)
        xml_str = xml.decode()
        return xml_str