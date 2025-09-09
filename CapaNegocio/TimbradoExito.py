class TimbradoExito:
    def __init__(self, idTimbradoExito: int, xmlTimbrado: str):
        self.idTimbradoExito = idTimbradoExito
        self.xmlTimbrado = xmlTimbrado

    def GenerarResultadoExito(self):
        # Devuelve el resultado de éxito en formato dict
        return {
            "id": self.idTimbradoExito,
            "exito": True,
            "xml_timbrado": self.xmlTimbrado,
        }