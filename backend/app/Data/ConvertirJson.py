from lxml import etree
from collections import OrderedDict
from decimal import Decimal
from datetime import datetime
from .cartaPorte import CartaPorteBuilder



class ConvertirJson:

    _SCHEMA_LOCATION_DEFAULT = (
        "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd "
        "http://www.sat.gob.mx/CartaPorte30 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xsd"
    )

    def __init__(self, datos_xml: dict, schema_location: str = _SCHEMA_LOCATION_DEFAULT):
        self.datos_xml = datos_xml
        self.schema_location = schema_location

    def GenerarXmlCFDI(self):
        # Declaración de namespaces
        nsmap = OrderedDict([
            ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
            ('cfdi', 'http://www.sat.gob.mx/cfd/4'),
            # Incluir namespace de CartaPorte desde el inicio para evitar manipular xmlns con set()
            ('cartaporte30', 'http://www.sat.gob.mx/CartaPorte30'),
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

        # Conceptos (soporta lista o único elemento)
        conceptos_block = comprobante_data.get("cfdi:Conceptos", {})
        conceptos_list = None
        if isinstance(conceptos_block, dict):
            conceptos_list = conceptos_block.get("cfdi:Concepto")
        else:
            conceptos_list = conceptos_block

        conceptos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Conceptos')

        # Normalizar a lista
        if conceptos_list is None:
            conceptos_list = []
        elif isinstance(conceptos_list, dict):
            conceptos_list = [conceptos_list]

        for concepto_data in conceptos_list:
            concepto_attrib = {k: str(v) for k, v in concepto_data.items() if v and not isinstance(v, dict)}
            concepto = etree.SubElement(conceptos, '{http://www.sat.gob.mx/cfd/4}Concepto', **concepto_attrib)

            # Impuestos a nivel Concepto (puede contener Traslados/Retenciones como lista o dict)
            concepto_impuestos_data = concepto_data.get("cfdi:Impuestos", {}) if isinstance(concepto_data, dict) else {}
            if concepto_impuestos_data:
                c_impuestos = etree.SubElement(concepto, '{http://www.sat.gob.mx/cfd/4}Impuestos')

                # Traslados
                if "cfdi:Traslados" in concepto_impuestos_data:
                    c_traslados = etree.SubElement(c_impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
                    t_node = concepto_impuestos_data["cfdi:Traslados"].get("cfdi:Traslado") if isinstance(concepto_impuestos_data.get("cfdi:Traslados"), dict) else concepto_impuestos_data.get("cfdi:Traslados")
                    if t_node is None:
                        t_list = []
                    elif isinstance(t_node, list):
                        t_list = t_node
                    else:
                        t_list = [t_node]

                    for c_traslado_data in t_list:
                        c_traslado_attrib = {k: str(v) for k, v in (c_traslado_data or {}).items() if v}
                        etree.SubElement(c_traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **c_traslado_attrib)

                # Retenciones
                if "cfdi:Retenciones" in concepto_impuestos_data:
                    c_retenciones = etree.SubElement(c_impuestos, '{http://www.sat.gob.mx/cfd/4}Retenciones')
                    r_node = concepto_impuestos_data["cfdi:Retenciones"].get("cfdi:Retencion") if isinstance(concepto_impuestos_data.get("cfdi:Retenciones"), dict) else concepto_impuestos_data.get("cfdi:Retenciones")
                    if r_node is None:
                        r_list = []
                    elif isinstance(r_node, list):
                        r_list = r_node
                    else:
                        r_list = [r_node]

                    for c_retencion_data in r_list:
                        c_retencion_attrib = {k: str(v) for k, v in (c_retencion_data or {}).items() if v}
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
            # Retenciones (puede ser lista o dict)
            if "cfdi:Retenciones" in impuestos_data:
                retenciones = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Retenciones')
                r_node = impuestos_data["cfdi:Retenciones"].get("cfdi:Retencion") if isinstance(impuestos_data.get("cfdi:Retenciones"), dict) else impuestos_data.get("cfdi:Retenciones")
                if r_node is None:
                    r_list = []
                elif isinstance(r_node, list):
                    r_list = r_node
                else:
                    r_list = [r_node]
                for retencion_data in r_list:
                    retencion_attrib = {k: str(v) for k, v in (retencion_data or {}).items() if v}
                    etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **retencion_attrib)

            # Traslados (puede ser lista o dict)
            if "cfdi:Traslados" in impuestos_data:
                traslados = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
                t_node = impuestos_data["cfdi:Traslados"].get("cfdi:Traslado") if isinstance(impuestos_data.get("cfdi:Traslados"), dict) else impuestos_data.get("cfdi:Traslados")
                if t_node is None:
                    t_list = []
                elif isinstance(t_node, list):
                    t_list = t_node
                else:
                    t_list = [t_node]
                for traslado_data in t_list:
                    traslado_attrib = {k: str(v) for k, v in (traslado_data or {}).items() if v}
                    etree.SubElement(traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **traslado_attrib)

        # Agregar complementos (si existen)
        comprobante = self._agregar_complementos(comprobante, comprobante_data)

        xml_cfdi = etree.tostring(comprobante, pretty_print=True, encoding='utf-8', xml_declaration=True)
        xml_resultado = xml_cfdi.decode('utf-8')
        return xml_resultado

    def _agregar_complementos(self, comprobante, comprobante_data):
        """Agrega complementos al CFDI si existen en los datos"""
        complemento_data = comprobante_data.get("cfdi:Complemento")
        if not complemento_data:
            return comprobante

        # Verificar si hay complemento de Carta Porte
        if "cartaporte30:CartaPorte" in complemento_data:
            comprobante = self._agregar_namespace_carta_porte(comprobante)
            comprobante = self._agregar_carta_porte(comprobante, complemento_data)

        # Aquí se pueden agregar más complementos en el futuro

        return comprobante
    
    def _agregar_carta_porte(self, comprobante, complemento_data):
        """Construye y agrega el complemento CartaPorte al CFDI"""
        carta_data = complemento_data.get("cartaporte30:CartaPorte", {})
        if not carta_data:
            return comprobante
        
        try:
            # Usar CartaPorteBuilder para construir el objeto CartaPorte desde JSON
            builder = CartaPorteBuilder(carta_data)
            carta_porte_obj = builder.construir()
            
            # Convertir el objeto CartaPorte a elemento XML usando satcfdi
            carta_xml = carta_porte_obj.to_xml()
            
            # Buscar o crear el nodo Complemento
            complemento_node = comprobante.find('{http://www.sat.gob.mx/cfd/4}Complemento')
            if complemento_node is None:
                complemento_node = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Complemento')
            
            # Anexar el elemento CartaPorte al Complemento
            if carta_xml is not None:
                complemento_node.append(carta_xml)
                
        except Exception as e:
            # Log del error para debugging
            print(f"Error al construir CartaPorte: {str(e)}")
            # Opcionalmente, puedes decidir si continuar sin el complemento o lanzar la excepción
            
        return comprobante

    def _agregar_namespace_carta_porte(self, comprobante):
        """Asegura que el namespace y schemaLocation de CartaPorte estén en el Comprobante.

        Añade el atributo xmlns:cartaporte30 y extiende xsi:schemaLocation si es necesario.
        """
        # Asegurar que xsi:schemaLocation incluya la entrada de CartaPorte
        schema_loc_attr = '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'
        existing = comprobante.get(schema_loc_attr, '') or ''
        add = ' http://www.sat.gob.mx/CartaPorte30 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xsd'
        if add.strip() not in existing:
            # mantener el existente y concatenar la entrada de CartaPorte
            new_val = (existing + add).strip()
            comprobante.set(schema_loc_attr, new_val)
        return comprobante
    