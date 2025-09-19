from lxml import etree
from collections import OrderedDict


class ConvertirJson:

    _SCHEMA_LOCATION_DEFAULT = (
        "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"
    )

    def __init__(self, datos_xml: dict, schema_location: str = _SCHEMA_LOCATION_DEFAULT):
        self.datos_xml = datos_xml
        self.schema_location = schema_location

    def GenerarXmlCFDI(self):
        # OrderedDict para intentar preservar el orden de declaración de namespaces
        nsmap = OrderedDict([
            ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
            ('cfdi', 'http://www.sat.gob.mx/cfd/4'),
        ])

        comprobante_data = self.datos_xml.get("cfdi:Comprobante", {})

        #  Agrega atributos unicamente con valor en json
        comprobante_attrib = {
            k: str(v)
            for k, v in comprobante_data.items()
            if v is not None and v != ""
            and not isinstance(v, dict)
            and not k.startswith("xmlns")
            and ":" not in k
            }
        # Crear elemento raíz Comprobante con namespaces
        comprobante = etree.Element('{http://www.sat.gob.mx/cfd/4}Comprobante', nsmap=nsmap)
        if self.schema_location:
            comprobante.set(
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                self.schema_location,
            )
        if 'Version' in comprobante_attrib:
            comprobante.set('Version', comprobante_attrib['Version'])
        for k, v in comprobante_attrib.items():
            if k == 'Version':
                continue
            comprobante.set(k, v)

        # Emisor
        emisor_data = comprobante_data.get("cfdi:Emisor", {})
        emisor_attrib = {k: str(v) for k, v in emisor_data.items() if v}
        # Coloca elemento Emisor
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

        # Impuestos a nivel Concepto
        concepto_impuestos_data = conceptos_data.get("cfdi:Impuestos", {}) if isinstance(conceptos_data, dict) else {}
        if concepto_impuestos_data:
            c_impuestos = etree.SubElement(concepto, '{http://www.sat.gob.mx/cfd/4}Impuestos')
            # Traslados
            if "cfdi:Traslados" in concepto_impuestos_data:
                c_traslados = etree.SubElement(c_impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
                c_traslado_data = concepto_impuestos_data["cfdi:Traslados"].get("cfdi:Traslado", {})
                c_traslado_attrib = {k: str(v) for k, v in c_traslado_data.items() if v}
                etree.SubElement(c_traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **c_traslado_attrib)
            # Retenciones
            if "cfdi:Retenciones" in concepto_impuestos_data:
                c_retenciones = etree.SubElement(c_impuestos, '{http://www.sat.gob.mx/cfd/4}Retenciones')
                c_retencion_data = concepto_impuestos_data["cfdi:Retenciones"].get("cfdi:Retencion", {})
                c_retencion_attrib = {k: str(v) for k, v in c_retencion_data.items() if v}
                etree.SubElement(c_retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **c_retencion_attrib)

        # Impuestos
        impuestos_data = comprobante_data.get("cfdi:Impuestos", {})
        if impuestos_data:
            # Atributos de totales (TotalImpuestosRetenidos / TotalImpuestosTrasladados) u otros permitidos
            impuestos_attrib = {
                k: str(v)
                for k, v in impuestos_data.items()
                if v is not None and v != "" and not isinstance(v, dict) and ":" not in k
            }

            # Calcular totales si faltan
            if ("TotalImpuestosTrasladados" not in impuestos_attrib or "TotalImpuestosRetenidos" not in impuestos_attrib):
                total_tras = None
                total_ret = None
                # Traslados suma
                try:
                    t_node = impuestos_data.get("cfdi:Traslados", {}).get("cfdi:Traslado")
                    if isinstance(t_node, dict):
                        importe_t = t_node.get("Importe") or t_node.get("importe")
                        if importe_t not in (None, ""):
                            total_tras = float(importe_t)
                except Exception:
                    pass
                # Retenciones suma
                try:
                    r_node = impuestos_data.get("cfdi:Retenciones", {}).get("cfdi:Retencion")
                    if isinstance(r_node, dict):
                        importe_r = r_node.get("Importe") or r_node.get("importe")
                        if importe_r not in (None, ""):
                            total_ret = float(importe_r)
                except Exception:
                    pass
                # Solo asignar si hay valor real y no existía
                if total_tras is not None and "TotalImpuestosTrasladados" not in impuestos_attrib:
                    impuestos_attrib["TotalImpuestosTrasladados"] = f"{total_tras:.2f}".rstrip('0').rstrip('.') if '.' in f"{total_tras:.2f}" else f"{total_tras:.2f}"
                if total_ret is not None and "TotalImpuestosRetenidos" not in impuestos_attrib:
                    impuestos_attrib["TotalImpuestosRetenidos"] = f"{total_ret:.2f}".rstrip('0').rstrip('.') if '.' in f"{total_ret:.2f}" else f"{total_ret:.2f}"
            impuestos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Impuestos', **impuestos_attrib)
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