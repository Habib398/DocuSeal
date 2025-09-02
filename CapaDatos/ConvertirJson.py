from lxml import etree

class ConvertirJson:
    def __init__(self, datos_xml: dict):
        self.datos_xml = datos_xml

    def GenerarXmlCFDI(self):
        nsmap = {
            'cfdi': 'http://www.sat.gob.mx/cfd/4',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        #Obtiene datos de json
        comprobante_data = self.datos_xml.get("Comprobante", {})

        # Declararion de atributos del xml
        comprobante = etree.Element(
            '{http://www.sat.gob.mx/cfd/4}Comprobante',
            nsmap=nsmap,
            Version="4.0",
            # Extrae atributos obligatorios
            Serie=comprobante_data.get("Serie", ""),
            Folio=comprobante_data.get("Folio", ""),
            Fecha=comprobante_data.get("Fecha", ""),
            Sello=comprobante_data.get("Sello", ""),
            NoCertificado=comprobante_data.get("NoCertificado", ""),
            Certificado=comprobante_data.get("Certificado", ""),
            SubTotal=str(comprobante_data.get("SubTotal", "")),
            Moneda=comprobante_data.get("Moneda", ""),
            Total=str(comprobante_data.get("Total", "")),
            TipoDeComprobante=comprobante_data.get("TipoDeComprobante", ""),
            LugarExpedicion=comprobante_data.get("LugarExpedicion", "")
        )

        # Atributos de emisor
        emisor_data = comprobante_data.get("Emisor", {})
        emisor = etree.SubElement(
            comprobante,
            '{http://www.sat.gob.mx/cfd/4}Emisor',
            Rfc=emisor_data.get("Rfc", ""),
            Nombre=emisor_data.get("Nombre", ""),
            RegimenFiscal=emisor_data.get("RegimenFiscal", "")
        )

        # atributos de receptor
        receptor_data = comprobante_data.get("Receptor", {})
        receptor = etree.SubElement(
            comprobante,
            '{http://www.sat.gob.mx/cfd/4}Receptor',
            Rfc=receptor_data.get("Rfc", ""),
            Nombre=receptor_data.get("Nombre", ""),
            UsoCFDI=receptor_data.get("UsoCFDI", "")
        )

        # Atributos de conceptos
        conceptos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Conceptos')
        # Recorre cadena de conceptos
        for concepto in comprobante_data.get("Conceptos", []):
            etree.SubElement(
                conceptos,
                '{http://www.sat.gob.mx/cfd/4}Concepto',
                ClaveProdServ=concepto.get("ClaveProdServ", ""),
                Cantidad=str(concepto.get("Cantidad", "")),
                ClaveUnidad=concepto.get("ClaveUnidad", ""),
                Descripcion=concepto.get("Descripcion", ""),
                ValorUnitario=str(concepto.get("ValorUnitario", "")),
                Importe=str(concepto.get("Importe", ""))
            )

        # Impuestos
        impuestos_data = comprobante_data.get("Impuestos", {})
        if impuestos_data:
            impuestos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Impuestos')
            traslados = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
            for traslado in impuestos_data.get("Traslados", []):
                etree.SubElement(
                    traslados,
                    '{http://www.sat.gob.mx/cfd/4}Traslado',
                    Base=str(traslado.get("Base", "")),
                    Impuesto=traslado.get("Impuesto", ""),
                    TipoFactor=traslado.get("TipoFactor", ""),
                    TasaOCuota=str(traslado.get("TasaOCuota", "")),
                    Importe=str(traslado.get("Importe", ""))
                )

        xml_cfdi = etree.tostring(comprobante, pretty_print=True, encoding='utf-8', xml_declaration=True)
        return xml_cfdi.decode('utf-8')
    