from lxml import etree

class ConvertirJson:
    def __init__(self, datos_xml: dict):
        self.datos_xml = datos_xml

    def GenerarXmlCFDI(self):
        nsmap = {
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        comprobante_data = self.datos_xml.get("cfdi:Comprobante", {})

        #  Agrega atributos con valor en json
        comprobante_attrib = {
            k: str(v)
            for k, v in comprobante_data.items()
            if v is not None and v != ""
            and not isinstance(v, dict)
            and not k.startswith("xmlns")
            and ":" not in k
            }
        
        comprobante = etree.Element(
            '{http://www.sat.gob.mx/cfd/4}Comprobante',
            nsmap=nsmap,
            **comprobante_attrib
        )
        if "xsi:schemaLocation" in comprobante_data and comprobante_data["xsi:schemaLocation"]:
            comprobante.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", comprobante_data["xsi:schemaLocation"])

        # Emisor
        emisor_data = comprobante_data.get("cfdi:Emisor", {})
        emisor_attrib = {k: str(v) for k, v in emisor_data.items() if v}
        etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Emisor', **emisor_attrib)

        # Receptor
        receptor_data = comprobante_data.get("cfdi:Receptor", {})
        receptor_attrib = {k: str(v) for k, v in receptor_data.items() if v}
        etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Receptor', **receptor_attrib)

        # Conceptos
        conceptos_data = comprobante_data.get("cfdi:Conceptos", {}).get("cfdi:Concepto", {})
        conceptos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Conceptos')
        concepto_attrib = {k: str(v) for k, v in conceptos_data.items() if v and not isinstance(v, dict)}
        concepto = etree.SubElement(conceptos, '{http://www.sat.gob.mx/cfd/4}Concepto', **concepto_attrib)

        # Impuestos
        impuestos_data = comprobante_data.get("cfdi:Impuestos", {})
        if impuestos_data:
            impuestos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Impuestos')
            # Retenciones
            if "cfdi:Retenciones" in impuestos_data:
                retenciones = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Retenciones')
                retencion_data = impuestos_data["cfdi:Retenciones"].get("cfdi:Retencion", {})
                retencion_attrib = {k: str(v) for k, v in retencion_data.items() if v}
                etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **retencion_attrib)
            # Traslados
            if "cfdi:Traslados" in impuestos_data:
                traslados = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
                traslado_data = impuestos_data["cfdi:Traslados"].get("cfdi:Traslado", {})
                traslado_attrib = {k: str(v) for k, v in traslado_data.items() if v}
                etree.SubElement(traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **traslado_attrib)

        xml_cfdi = etree.tostring(comprobante, pretty_print=True, encoding='utf-8', xml_declaration=True)
        xml_resultado = xml_cfdi.decode('utf-8')
        print(xml_resultado)
        return xml_resultado