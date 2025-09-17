import lxml.etree as ET

class ValidadorXMLCFDI:
    @staticmethod
    def validar_xml(xml_str: str, xsd_path: str) -> dict:
        """
        Valida la estructura del XML CFDI contra el XSD oficial.
        Args:
            xml_str (str): XML a validar.
            xsd_path (str): Ruta al archivo XSD del SAT.
        Returns:
            dict: {'valido': bool, 'errores': [str]}
        """
        try:
            xml_doc = ET.fromstring(xml_str.encode('utf-8'))
            with open(xsd_path, 'rb') as f:
                xsd_doc = ET.parse(f)
            xsd = ET.XMLSchema(xsd_doc)
            valido = xsd.validate(xml_doc)
            errores = []
            if not valido:
                for error in xsd.error_log:
                    errores.append(str(error))
            return {'valido': valido, 'errores': errores}
        except Exception as e:
            return {'valido': False, 'errores': [str(e)]}
