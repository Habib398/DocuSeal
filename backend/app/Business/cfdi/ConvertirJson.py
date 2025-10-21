from lxml import etree
from collections import OrderedDict


class ConvertirJson:

    _SCHEMA_LOCATION_DEFAULT = (
        "http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd "
        "http://www.sat.gob.mx/CartaPorte31 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte31.xsd"
    )

    def __init__(self, xml: dict, schema_location: str = _SCHEMA_LOCATION_DEFAULT):
        self.datos_xml = xml
        self.schema_location = schema_location

    def tiene_carta_porte(self) -> bool:
        """
        Verifica si el JSON tiene complemento Carta Porte.
        """
        comprobante_data = self.datos_xml.get("cfdi:Comprobante", self.datos_xml)
        complemento_data = comprobante_data.get("cfdi:Complemento") or comprobante_data.get("Complemento", {})
        carta_porte_data = complemento_data.get("cartaporte30:CartaPorte") or complemento_data.get("CartaPorte")
        return carta_porte_data is not None

    def GenerarXmlCFDI(self):
        # OrderedDict para intentar preservar el orden de declaración de namespaces
        nsmap = OrderedDict([
            ('xsi', 'http://www.w3.org/2001/XMLSchema-instance'),
            ('cfdi', 'http://www.sat.gob.mx/cfd/4'),
            ('cartaporte31', 'http://www.sat.gob.mx/CartaPorte31'),
        ])

        comprobante_data = self.datos_xml.get("cfdi:Comprobante", self.datos_xml)

        #  Agrega atributos unicamente con valor en json
        comprobante_attrib = {
            k: str(v)
            for k, v in comprobante_data.items()
            if v is not None and (v != "" if isinstance(v, str) else True)
            and not isinstance(v, dict)
            and not isinstance(v, list)
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
        emisor_data = comprobante_data.get("cfdi:Emisor") or comprobante_data.get("Emisor", {})
        emisor_attrib = {k: str(v) for k, v in emisor_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
        # Coloca elemento Emisor
        etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Emisor', **emisor_attrib)

        # Receptor
        receptor_data = comprobante_data.get("cfdi:Receptor") or comprobante_data.get("Receptor", {})
        receptor_attrib = {k: str(v) for k, v in receptor_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
        etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Receptor', **receptor_attrib)

        # Conceptos
        conceptos_data = comprobante_data.get("cfdi:Conceptos") or comprobante_data.get("Conceptos", {})
        if isinstance(conceptos_data, list) and conceptos_data:
            # Si es una lista de conceptos
            concepto_data = conceptos_data[0]  # Tomar el primer concepto
        else:
            # Si es un diccionario o está vacío
            concepto_data = conceptos_data if isinstance(conceptos_data, dict) else {}
        
        # Extraer datos reales del concepto si está envuelto
        concepto_data = concepto_data.get("cfdi:Concepto") or concepto_data.get("Concepto") or concepto_data
        
        if isinstance(concepto_data, list):
            concepto_data = concepto_data[0] if concepto_data else {}
        
        conceptos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Conceptos')
        concepto_attrib = {k: str(v) for k, v in concepto_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
        concepto = etree.SubElement(conceptos, '{http://www.sat.gob.mx/cfd/4}Concepto', **concepto_attrib)

        # Impuestos a nivel Concepto
        concepto_impuestos_data = concepto_data.get("cfdi:Impuestos") or concepto_data.get("Impuestos", {})
        if concepto_impuestos_data:
            c_impuestos = etree.SubElement(concepto, '{http://www.sat.gob.mx/cfd/4}Impuestos')
            # Traslados
            traslados_data = concepto_impuestos_data.get("cfdi:Traslados") or concepto_impuestos_data.get("Traslados")
            if traslados_data:
                c_traslados = etree.SubElement(c_impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
                if isinstance(traslados_data, list) and traslados_data:
                    for traslado_data in traslados_data:
                        c_traslado_attrib = {k: str(v) for k, v in traslado_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(c_traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **c_traslado_attrib)
                elif isinstance(traslados_data, dict):
                    traslado_data = traslados_data.get("cfdi:Traslado") or traslados_data.get("Traslado") or traslados_data
                    if isinstance(traslado_data, dict):
                        c_traslado_attrib = {k: str(v) for k, v in traslado_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(c_traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **c_traslado_attrib)
                    elif isinstance(traslado_data, list):
                        for t_data in traslado_data:
                            c_traslado_attrib = {k: str(v) for k, v in t_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                            etree.SubElement(c_traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **c_traslado_attrib)
            # Retenciones
            retenciones_data = concepto_impuestos_data.get("cfdi:Retenciones") or concepto_impuestos_data.get("Retenciones")
            if retenciones_data:
                c_retenciones = etree.SubElement(c_impuestos, '{http://www.sat.gob.mx/cfd/4}Retenciones')
                if isinstance(retenciones_data, list) and retenciones_data:
                    for retencion_data in retenciones_data:
                        c_retencion_attrib = {k: str(v) for k, v in retencion_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(c_retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **c_retencion_attrib)
                elif isinstance(retenciones_data, dict):
                    retencion_data = retenciones_data.get("cfdi:Retencion") or retenciones_data.get("Retencion") or retenciones_data
                    if isinstance(retencion_data, dict):
                        c_retencion_attrib = {k: str(v) for k, v in retencion_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(c_retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **c_retencion_attrib)
                    elif isinstance(retencion_data, list):
                        for r_data in retencion_data:
                            c_retencion_attrib = {k: str(v) for k, v in r_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                            etree.SubElement(c_retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **c_retencion_attrib)

        # Impuestos
        impuestos_data = comprobante_data.get("cfdi:Impuestos") or comprobante_data.get("Impuestos", {})
        if impuestos_data:
            # Atributos de totales (TotalImpuestosRetenidos / TotalImpuestosTrasladados) u otros permitidos
            impuestos_attrib = {
                k: str(v)
                for k, v in impuestos_data.items()
                if v is not None and v != "" and not isinstance(v, dict) and ":" not in k
            }

            # Calcular totales si faltan o si es tipo T/P (traslados/pagos)
            tipo_comprobante = comprobante_data.get("TipoDeComprobante", "I")
            if ("TotalImpuestosTrasladados" not in impuestos_attrib or "TotalImpuestosRetenidos" not in impuestos_attrib) or tipo_comprobante in ["T", "P"]:
                total_tras = None
                total_ret = None
                # Traslados suma
                try:
                    traslados_data = impuestos_data.get("cfdi:Traslados") or impuestos_data.get("Traslados")
                    if traslados_data:
                        if isinstance(traslados_data, list) and traslados_data:
                            total_tras = sum(float(t.get("Importe", 0) or t.get("importe", 0)) for t in traslados_data if isinstance(t, dict))
                        elif isinstance(traslados_data, dict):
                            traslado_data = traslados_data.get("cfdi:Traslado") or traslados_data.get("Traslado") or traslados_data
                            if isinstance(traslado_data, dict):
                                importe_t = traslado_data.get("Importe") or traslado_data.get("importe")
                                if importe_t not in (None, ""):
                                    total_tras = float(importe_t)
                            elif isinstance(traslado_data, list):
                                total_tras = sum(float(t.get("Importe", 0) or t.get("importe", 0)) for t in traslado_data if isinstance(t, dict))
                except Exception:
                    pass
                # Retenciones suma
                try:
                    retenciones_data = impuestos_data.get("cfdi:Retenciones") or impuestos_data.get("Retenciones")
                    if retenciones_data:
                        if isinstance(retenciones_data, list) and retenciones_data:
                            total_ret = sum(float(r.get("Importe", 0) or r.get("importe", 0)) for r in retenciones_data if isinstance(r, dict))
                        elif isinstance(retenciones_data, dict):
                            retencion_data = retenciones_data.get("cfdi:Retencion") or retenciones_data.get("Retencion") or retenciones_data
                            if isinstance(retencion_data, dict):
                                importe_r = retencion_data.get("Importe") or retencion_data.get("importe")
                                if importe_r not in (None, ""):
                                    total_ret = float(importe_r)
                            elif isinstance(retencion_data, list):
                                total_ret = sum(float(r.get("Importe", 0) or r.get("importe", 0)) for r in retencion_data if isinstance(r, dict))
                except Exception:
                    pass
                # Solo asignar si hay valor real y no existía, o siempre para T/P
                if total_tras is not None and ("TotalImpuestosTrasladados" not in impuestos_attrib or tipo_comprobante in ["T", "P"]):
                    impuestos_attrib["TotalImpuestosTrasladados"] = f"{total_tras:.2f}".rstrip('0').rstrip('.') if '.' in f"{total_tras:.2f}" else f"{total_tras:.2f}"
                if total_ret is not None and ("TotalImpuestosRetenidos" not in impuestos_attrib or tipo_comprobante in ["T", "P"]):
                    impuestos_attrib["TotalImpuestosRetenidos"] = f"{total_ret:.2f}".rstrip('0').rstrip('.') if '.' in f"{total_ret:.2f}" else f"{total_ret:.2f}"
            impuestos = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Impuestos', **impuestos_attrib)
            # Retenciones
            retenciones_data = impuestos_data.get("cfdi:Retenciones") or impuestos_data.get("Retenciones")
            if retenciones_data:
                retenciones = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Retenciones')
                if isinstance(retenciones_data, list) and retenciones_data:
                    for retencion_data in retenciones_data:
                        retencion_attrib = {k: str(v) for k, v in retencion_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **retencion_attrib)
                elif isinstance(retenciones_data, dict):
                    retencion_data = retenciones_data.get("cfdi:Retencion") or retenciones_data.get("Retencion") or retenciones_data
                    if isinstance(retencion_data, dict):
                        retencion_attrib = {k: str(v) for k, v in retencion_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **retencion_attrib)
                    elif isinstance(retencion_data, list):
                        for r_data in retencion_data:
                            retencion_attrib = {k: str(v) for k, v in r_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                            etree.SubElement(retenciones, '{http://www.sat.gob.mx/cfd/4}Retencion', **retencion_attrib)
            # Traslados
            traslados_data = impuestos_data.get("cfdi:Traslados") or impuestos_data.get("Traslados")
            if traslados_data:
                traslados = etree.SubElement(impuestos, '{http://www.sat.gob.mx/cfd/4}Traslados')
                if isinstance(traslados_data, list) and traslados_data:
                    for traslado_data in traslados_data:
                        traslado_attrib = {k: str(v) for k, v in traslado_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **traslado_attrib)
                elif isinstance(traslados_data, dict):
                    traslado_data = traslados_data.get("cfdi:Traslado") or traslados_data.get("Traslado") or traslados_data
                    if isinstance(traslado_data, dict):
                        traslado_attrib = {k: str(v) for k, v in traslado_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **traslado_attrib)
                    elif isinstance(traslado_data, list):
                        for t_data in traslado_data:
                            traslado_attrib = {k: str(v) for k, v in t_data.items() if v is not None and (v != "" if isinstance(v, str) else True) and not isinstance(v, dict) and not isinstance(v, list)}
                            etree.SubElement(traslados, '{http://www.sat.gob.mx/cfd/4}Traslado', **traslado_attrib)

        # CfdiRelacionados
        cfdi_relacionados_data = comprobante_data.get("CfdiRelacionados")
        if cfdi_relacionados_data:
            tipo_relacion = cfdi_relacionados_data.get("tipo_relacion")
            cfdi_relacionado = cfdi_relacionados_data.get("cfdi_relacionado")
            if tipo_relacion and cfdi_relacionado:
                cfdi_rel = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}CfdiRelacionados', TipoRelacion=tipo_relacion)
                etree.SubElement(cfdi_rel, '{http://www.sat.gob.mx/cfd/4}CfdiRelacionado', UUID=cfdi_relacionado)

        # Complemento
        complemento_data = comprobante_data.get("cfdi:Complemento") or comprobante_data.get("Complemento", {})
        if complemento_data:
            complemento = etree.SubElement(comprobante, '{http://www.sat.gob.mx/cfd/4}Complemento')
            
            # Carta Porte
            carta_porte_data = complemento_data.get("cartaporte31:CartaPorte") or complemento_data.get("cartaporte30:CartaPorte") or complemento_data.get("CartaPorte")
            if carta_porte_data:
                self._add_carta_porte(complemento, carta_porte_data)

        xml_cfdi = etree.tostring(comprobante, pretty_print=True, encoding='utf-8', xml_declaration=True)
        xml_resultado = xml_cfdi.decode('utf-8')
        xml_resultado = xml_resultado.replace("<?xml version='1.0' encoding='UTF-8'?>", "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        
        # Ajuste para compatibilidad: cambiar namespace de cartaporte31 a cartaporte30 para signing
        xml_resultado = xml_resultado.replace('cartaporte31', 'cartaporte30')
        xml_resultado = xml_resultado.replace('http://www.sat.gob.mx/CartaPorte31', 'http://www.sat.gob.mx/CartaPorte30')
        
        return xml_resultado

    def _add_carta_porte(self, complemento, carta_porte_data):
        """
        Agrega el elemento CartaPorte al complemento.
        """
        # Atributos del CartaPorte
        carta_porte_attrib = {k: str(v) for k, v in carta_porte_data.items() if k not in ['cartaporte31:Ubicaciones', 'Ubicaciones', 'cartaporte31:Mercancias', 'Mercancias', 'cartaporte31:FiguraTransporte', 'FiguraTransporte'] and v is not None and not isinstance(v, dict) and not isinstance(v, list)}
        carta_porte = etree.SubElement(complemento, '{http://www.sat.gob.mx/CartaPorte31}CartaPorte', **carta_porte_attrib)
        
        # Ubicaciones
        ubicaciones_data = carta_porte_data.get('cartaporte31:Ubicaciones') or carta_porte_data.get('cartaporte30:Ubicaciones') or carta_porte_data.get('Ubicaciones')
        if ubicaciones_data and isinstance(ubicaciones_data, dict):
            ubicaciones = etree.SubElement(carta_porte, '{http://www.sat.gob.mx/CartaPorte31}Ubicaciones')
            ubicacion_list = ubicaciones_data.get('cartaporte31:Ubicacion') or ubicaciones_data.get('cartaporte30:Ubicacion') or ubicaciones_data.get('Ubicacion')
            if isinstance(ubicacion_list, list):
                for ubicacion_data in ubicacion_list:
                    if isinstance(ubicacion_data, dict):
                        ubicacion_attrib = {k: str(v) for k, v in ubicacion_data.items() if k != 'cartaporte31:Domicilio' and k != 'cartaporte30:Domicilio' and v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                        ubicacion = etree.SubElement(ubicaciones, '{http://www.sat.gob.mx/CartaPorte31}Ubicacion', **ubicacion_attrib)
                        # Domicilio
                        domicilio_data = ubicacion_data.get('cartaporte31:Domicilio') or ubicacion_data.get('cartaporte30:Domicilio') or ubicacion_data.get('Domicilio')
                        if domicilio_data and isinstance(domicilio_data, dict):
                            domicilio_attrib = {k: str(v) for k, v in domicilio_data.items() if v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                            etree.SubElement(ubicacion, '{http://www.sat.gob.mx/CartaPorte31}Domicilio', **domicilio_attrib)
        
        # Mercancias
        mercancias_data = carta_porte_data.get('cartaporte31:Mercancias') or carta_porte_data.get('cartaporte30:Mercancias') or carta_porte_data.get('Mercancias')
        if mercancias_data and isinstance(mercancias_data, dict):
            mercancias_attrib = {k: str(v) for k, v in mercancias_data.items() if k not in ['cartaporte31:Mercancia', 'cartaporte30:Mercancia', 'Mercancia', 'cartaporte31:Autotransporte', 'cartaporte30:Autotransporte'] and v is not None and not isinstance(v, dict) and not isinstance(v, list)}
            mercancias = etree.SubElement(carta_porte, '{http://www.sat.gob.mx/CartaPorte31}Mercancias', **mercancias_attrib)
            mercancia_data = mercancias_data.get('cartaporte31:Mercancia') or mercancias_data.get('cartaporte30:Mercancia') or mercancias_data.get('Mercancia')
            if mercancia_data and isinstance(mercancia_data, dict):
                mercancia_attrib = {k: str(v) for k, v in mercancia_data.items() if v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                etree.SubElement(mercancias, '{http://www.sat.gob.mx/CartaPorte31}Mercancia', **mercancia_attrib)
            # Autotransporte
            autotransporte_data = mercancias_data.get('cartaporte31:Autotransporte') or mercancias_data.get('cartaporte30:Autotransporte') or mercancias_data.get('Autotransporte')
            if autotransporte_data and isinstance(autotransporte_data, dict):
                autotransporte_attrib = {k: str(v) for k, v in autotransporte_data.items() if k not in ['cartaporte31:IdentificacionVehicular', 'cartaporte30:IdentificacionVehicular', 'cartaporte31:Seguros', 'cartaporte30:Seguros', 'cartaporte31:Remolques', 'cartaporte30:Remolques'] and v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                autotransporte = etree.SubElement(mercancias, '{http://www.sat.gob.mx/CartaPorte31}Autotransporte', **autotransporte_attrib)
                # IdentificacionVehicular
                ident_data = autotransporte_data.get('cartaporte31:IdentificacionVehicular') or autotransporte_data.get('cartaporte30:IdentificacionVehicular') or autotransporte_data.get('IdentificacionVehicular')
                if ident_data and isinstance(ident_data, dict):
                    ident_attrib = {k: str(v) for k, v in ident_data.items() if v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                    etree.SubElement(autotransporte, '{http://www.sat.gob.mx/CartaPorte31}IdentificacionVehicular', **ident_attrib)
                # Seguros
                seguros_data = autotransporte_data.get('cartaporte31:Seguros') or autotransporte_data.get('cartaporte30:Seguros') or autotransporte_data.get('Seguros')
                if seguros_data and isinstance(seguros_data, dict):
                    seguros_attrib = {k: str(v) for k, v in seguros_data.items() if v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                    etree.SubElement(autotransporte, '{http://www.sat.gob.mx/CartaPorte31}Seguros', **seguros_attrib)
                # Remolques
                remolques_data = autotransporte_data.get('cartaporte31:Remolques') or autotransporte_data.get('cartaporte30:Remolques') or autotransporte_data.get('Remolques')
                if remolques_data and isinstance(remolques_data, dict):
                    remolques = etree.SubElement(autotransporte, '{http://www.sat.gob.mx/CartaPorte31}Remolques')
                    remolque_data = remolques_data.get('cartaporte31:Remolque') or remolques_data.get('cartaporte30:Remolque') or remolques_data.get('Remolque')
                    if remolque_data and isinstance(remolque_data, dict):
                        remolque_attrib = {k: str(v) for k, v in remolque_data.items() if v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                        etree.SubElement(remolques, '{http://www.sat.gob.mx/CartaPorte31}Remolque', **remolque_attrib)
        
        # FiguraTransporte
        figura_data = carta_porte_data.get('cartaporte31:FiguraTransporte') or carta_porte_data.get('cartaporte30:FiguraTransporte') or carta_porte_data.get('FiguraTransporte')
        if figura_data and isinstance(figura_data, dict):
            figura = etree.SubElement(carta_porte, '{http://www.sat.gob.mx/CartaPorte31}FiguraTransporte')
            tipos_figura_data = figura_data.get('cartaporte31:TiposFigura') or figura_data.get('cartaporte30:TiposFigura') or figura_data.get('TiposFigura')
            if tipos_figura_data and isinstance(tipos_figura_data, dict):
                tipos_attrib = {k: str(v) for k, v in tipos_figura_data.items() if v is not None and not isinstance(v, dict) and not isinstance(v, list)}
                etree.SubElement(figura, '{http://www.sat.gob.mx/CartaPorte31}TiposFigura', **tipos_attrib)