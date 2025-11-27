from satcfdi.create.cfd import cfdi40
from typing import Dict, Any, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from satcfdi.create.cfd import pago20


class ConvertirJson:
    
    def __init__(self):
        self.comprobante = None
        self.datos_emisor = None
        self.datos_receptor = None
        self.conceptos = []
        self.cfdi_relacionados = None
    
    def convertir_a_cfdi(self, datos_json: Dict[str, Any]) -> cfdi40.Comprobante:
        # Verificar si es un comprobante de pago
        comprobante_data = datos_json.get('datosXML', {}).get('cfdi:Comprobante', datos_json.get('cfdi:Comprobante', {}))
        tipo_comprobante = comprobante_data.get('TipoDeComprobante', 'I')
        
        # Si es un comprobante de pago, usar método especial
        if tipo_comprobante == 'P':
            return self._convertir_comprobante_pago(datos_json)
        
        # Para otros tipos de comprobante, continuar con el flujo normal
        self.datos_emisor = self._procesar_emisor(datos_json)
        self.datos_receptor = self._procesar_receptor(datos_json)
        self.conceptos = self._procesar_conceptos(datos_json)
        self.cfdi_relacionados = self._procesar_cfdi_relacionados(datos_json)
        atributos_comprobante = self._procesar_atributos_comprobante(datos_json)
        
        # Extraer y eliminar lugar_expedicion del diccionario para pasarlo como argumento
        lugar_expedicion = atributos_comprobante.pop('lugar_expedicion')
        self.comprobante = cfdi40.Comprobante(
            emisor=self.datos_emisor,
            lugar_expedicion=lugar_expedicion,
            receptor=self.datos_receptor,
            conceptos=self.conceptos,
            cfdi_relacionados=self.cfdi_relacionados,
            **atributos_comprobante
        )
        
        # Procesar complementos si se detectan
        self._procesar_complementos(datos_json)
        
        return self.comprobante
    
    def _procesar_emisor(self, datos_json: Dict[str, Any]) -> cfdi40.Emisor:
        emisor_data = None

        if datos_json.get('datosXML', {}).get('cfdi:Comprobante', {}).get('cfdi:Emisor'):
            emisor_data = datos_json['datosXML']['cfdi:Comprobante']['cfdi:Emisor']
        elif datos_json.get('datosXML', {}).get('emisor'):
            emisor_data = datos_json['datosXML']['emisor']
        elif datos_json.get('emisor'):
            emisor_data = datos_json['emisor']
        
        if not emisor_data:
            raise ValueError("Faltan datos del emisor en el JSON")
        
        # Extraer RFC (campo obligatorio)
        rfc = emisor_data.get('Rfc') or emisor_data.get('rfc') or emisor_data.get('RFC')
        if not rfc:
            raise ValueError("El RFC del emisor es obligatorio")
        
        # Extraer Nombre (campo obligatorio)
        nombre = emisor_data.get('Nombre') or emisor_data.get('nombre')
        if not nombre:
            raise ValueError("El nombre del emisor es obligatorio")
        
        # Extraer Régimen Fiscal (campo obligatorio)
        regimen_fiscal = (emisor_data.get('RegimenFiscal') or 
                         emisor_data.get('regimen_fiscal') or 
                         emisor_data.get('RegimenFiscal'))
        if not regimen_fiscal:
            raise ValueError("El régimen fiscal del emisor es obligatorio")
        
        # Crear objeto Emisor con los datos extraídos
        emisor = cfdi40.Emisor(
            rfc=rfc,
            nombre=nombre,
            regimen_fiscal=regimen_fiscal
        )
        
        return emisor
    
    def _procesar_receptor(self, datos_json: Dict[str, Any]) -> cfdi40.Receptor:
        receptor_data = None
        
        # Buscar datos del receptor en diferentes ubicaciones
        if datos_json.get('datosXML', {}).get('cfdi:Comprobante', {}).get('cfdi:Receptor'):
            receptor_data = datos_json['datosXML']['cfdi:Comprobante']['cfdi:Receptor']
        elif datos_json.get('datosXML', {}).get('receptor'):
            receptor_data = datos_json['datosXML']['receptor']
        elif datos_json.get('receptor'):
            receptor_data = datos_json['receptor']
        
        if not receptor_data:
            raise ValueError("No se encontraron datos del receptor en el JSON")
        
        # Extraer RFC (campo obligatorio)
        rfc = receptor_data.get('Rfc') or receptor_data.get('rfc') or receptor_data.get('RFC')
        if not rfc:
            raise ValueError("El RFC del receptor es obligatorio")
        
        # Extraer Nombre (campo obligatorio)
        nombre = receptor_data.get('Nombre') or receptor_data.get('nombre')
        if not nombre:
            raise ValueError("El nombre del receptor es obligatorio")
        
        # Extraer Domicilio Fiscal Receptor (campo obligatorio CFDI 4.0)
        domicilio_fiscal = (receptor_data.get('DomicilioFiscalReceptor') or 
                           receptor_data.get('domicilio_fiscal_receptor'))
        if not domicilio_fiscal:
            raise ValueError("El domicilio fiscal del receptor es obligatorio")
        
        # Extraer Régimen Fiscal Receptor (campo obligatorio CFDI 4.0)
        regimen_fiscal = (receptor_data.get('RegimenFiscalReceptor') or 
                         receptor_data.get('regimen_fiscal_receptor'))
        if not regimen_fiscal:
            raise ValueError("El régimen fiscal del receptor es obligatorio")
        
        # Extraer Uso CFDI (campo obligatorio)
        uso_cfdi = receptor_data.get('UsoCFDI') or receptor_data.get('uso_cfdi')
        if not uso_cfdi:
            raise ValueError("El uso CFDI del receptor es obligatorio")
        
        # Crear objeto Receptor con los datos extraídos
        receptor = cfdi40.Receptor(
            rfc=rfc,
            nombre=nombre,
            domicilio_fiscal_receptor=domicilio_fiscal,
            regimen_fiscal_receptor=regimen_fiscal,
            uso_cfdi=uso_cfdi
        )
        
        return receptor
    
    def _procesar_cfdi_relacionados(self, datos_json: Dict[str, Any]) -> Union[List[cfdi40.CfdiRelacionados], cfdi40.CfdiRelacionados, None]:
        """
        Procesa los CFDI relacionados desde el JSON.
        Retorna una lista de objetos CfdiRelacionados o un solo objeto, o None si no hay.
        """
        relacionados_data = None
        
        # Buscar datos de CFDI relacionados en diferentes ubicaciones
        if datos_json.get('datosXML', {}).get('cfdi:Comprobante', {}).get('cfdi:CfdiRelacionados'):
            relacionados_data = datos_json['datosXML']['cfdi:Comprobante']['cfdi:CfdiRelacionados']
        elif datos_json.get('datosXML', {}).get('CfdiRelacionados'):
            relacionados_data = datos_json['datosXML']['CfdiRelacionados']
        elif datos_json.get('datosXML', {}).get('cfdi_relacionados'):
            relacionados_data = datos_json['datosXML']['cfdi_relacionados']
        elif datos_json.get('cfdi_relacionados'):
            relacionados_data = datos_json['cfdi_relacionados']
        
        # Si no hay CFDI relacionados, retornar None
        if not relacionados_data:
            return None
        
        # Asegurar que sea una lista
        if not isinstance(relacionados_data, list):
            relacionados_data = [relacionados_data]
        
        cfdi_relacionados_list = []
        
        for idx, rel_data in enumerate(relacionados_data, 1):
            # Extraer TipoRelacion (obligatorio)
            tipo_relacion = (rel_data.get('TipoRelacion') or 
                           rel_data.get('tipo_relacion') or
                           rel_data.get('TipoRelacion'))
            
            if not tipo_relacion:
                raise ValueError(f"TipoRelacion es obligatorio en CfdiRelacionados #{idx}")
            
            # Extraer uno o mas CfdiRelacionado (obligatorio)
            cfdi_relacionado = None
            
            # Buscar en diferentes formatos posibles
            if rel_data.get('cfdi:CfdiRelacionado'):
                cfdi_relacionado = rel_data['cfdi:CfdiRelacionado']
            elif rel_data.get('CfdiRelacionado'):
                cfdi_relacionado = rel_data['CfdiRelacionado']
            elif rel_data.get('cfdi_relacionado'):
                cfdi_relacionado = rel_data['cfdi_relacionado']
            elif rel_data.get('UUID'):
                cfdi_relacionado = rel_data['UUID']
            elif rel_data.get('uuid'):
                cfdi_relacionado = rel_data['uuid']
            
            if not cfdi_relacionado:
                raise ValueError(f"CfdiRelacionado (UUID) es obligatorio en CfdiRelacionados #{idx}")
            
            # Si CfdiRelacionado es un diccionario o lista de diccionarios, extraer UUID
            uuids = []
            if isinstance(cfdi_relacionado, list):
                for item in cfdi_relacionado:
                    if isinstance(item, dict):
                        uuid = item.get('UUID') or item.get('uuid')
                        if uuid:
                            uuids.append(uuid)
                    elif isinstance(item, str):
                        uuids.append(item)
            elif isinstance(cfdi_relacionado, dict):
                uuid = cfdi_relacionado.get('UUID') or cfdi_relacionado.get('uuid')
                if uuid:
                    uuids.append(uuid)
            elif isinstance(cfdi_relacionado, str):
                uuids.append(cfdi_relacionado)
            
            if not uuids:
                raise ValueError(f"No se encontraron UUIDs válidos en CfdiRelacionados #{idx}")
            
            # Crear objeto CfdiRelacionados
            # Si hay un solo UUID, pasar como string; si hay varios, pasar como lista
            cfdi_rel_obj = cfdi40.CfdiRelacionados(
                tipo_relacion=tipo_relacion,
                cfdi_relacionado=uuids if len(uuids) > 1 else uuids[0]
            )
            
            cfdi_relacionados_list.append(cfdi_rel_obj)
        
        # Si solo hay un objeto, retornarlo directamente; si hay varios, retornar la lista
        if len(cfdi_relacionados_list) == 0:
            return None
        elif len(cfdi_relacionados_list) == 1:
            return cfdi_relacionados_list[0]
        else:
            return cfdi_relacionados_list
    
    def _procesar_atributos_comprobante(self, datos_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa los atributos principales del comprobante desde el JSON.
        Nota: SubTotal, Total y Descuento se calculan automáticamente por satcfdi
        a partir de los conceptos, por lo que NO se incluyen en los atributos.
        """
        comprobante_data = None
        atributos = {}
        
        # Buscar datos del comprobante en diferentes ubicaciones
        if datos_json.get('datosXML', {}).get('cfdi:Comprobante'):
            comprobante_data = datos_json['datosXML']['cfdi:Comprobante']
        elif datos_json.get('xml'):
            comprobante_data = datos_json['xml']
        elif datos_json.get('datosXML'):
            comprobante_data = datos_json['datosXML']
        
        if not comprobante_data:
            raise ValueError("No se encontraron datos del comprobante en el JSON")
        
        # Lugar de Expedición (campo obligatorio)
        lugar_expedicion = (comprobante_data.get('LugarExpedicion') or 
                           comprobante_data.get('lugar_expedicion'))
        if not lugar_expedicion:
            raise ValueError("El lugar de expedición es obligatorio")
        atributos['lugar_expedicion'] = lugar_expedicion
        
        # Moneda (campo obligatorio, default='MXN')
        moneda = comprobante_data.get('Moneda') or comprobante_data.get('moneda')
        if moneda:
            atributos['moneda'] = moneda
        
        # Tipo de Comprobante (campo obligatorio, default='I')
        tipo_comprobante = (comprobante_data.get('TipoDeComprobante') or 
                           comprobante_data.get('tipo_de_comprobante') or 
                           comprobante_data.get('TipoComprobante'))
        if tipo_comprobante:
            atributos['tipo_de_comprobante'] = tipo_comprobante
        
        # Exportación (campo obligatorio CFDI 4.0, default='01')
        exportacion = comprobante_data.get('Exportacion') or comprobante_data.get('exportacion')
        if exportacion:
            atributos['exportacion'] = exportacion
        
        # Serie (opcional)
        serie = comprobante_data.get('Serie') or comprobante_data.get('serie')
        if serie:
            atributos['serie'] = serie
        
        # Folio (opcional)
        folio = comprobante_data.get('Folio') or comprobante_data.get('folio')
        if folio:
            atributos['folio'] = folio
        
        # Fecha (opcional, si no se proporciona usa la fecha actual)
        fecha = comprobante_data.get('Fecha') or comprobante_data.get('fecha')
        if fecha:
            from datetime import datetime
            try:
                atributos['fecha'] = datetime.fromisoformat(fecha)
            except ValueError:
                # Si no es formato ISO, intentar otros formatos comunes
                try:
                    atributos['fecha'] = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValueError(f"Formato de fecha inválido: {fecha}. Use formato ISO 8601 (YYYY-MM-DDTHH:MM:SS)")
        
        # Forma de Pago (condicional)
        forma_pago = comprobante_data.get('FormaPago') or comprobante_data.get('forma_pago')
        if forma_pago:
            atributos['forma_pago'] = forma_pago
        
        # Condiciones de Pago (opcional)
        condiciones_pago = comprobante_data.get('CondicionesDePago') or comprobante_data.get('condiciones_de_pago')
        if condiciones_pago:
            atributos['condiciones_de_pago'] = condiciones_pago
        
        # Tipo de Cambio (condicional - obligatorio si moneda != MXN)
        tipo_cambio = comprobante_data.get('TipoCambio') or comprobante_data.get('tipo_cambio')
        if tipo_cambio:
            atributos['tipo_cambio'] = tipo_cambio
        
        # Método de Pago (condicional)
        metodo_pago = comprobante_data.get('MetodoPago') or comprobante_data.get('metodo_pago')
        if metodo_pago:
            atributos['metodo_pago'] = metodo_pago
        
        # Confirmación (opcional)
        confirmacion = comprobante_data.get('Confirmacion') or comprobante_data.get('confirmacion')
        if confirmacion:
            atributos['confirmacion'] = confirmacion
        
        # Filtrar campos que no son atributos del comprobante (metadatos XML)
        campos_a_excluir = {
            'xmlns:cfdi', 'xmlns:xsi', 'xsi:schemaLocation', 'Version',
            'cfdi:Emisor', 'cfdi:Receptor', 'cfdi:Conceptos', 'cfdi:Impuestos',
            'cfdi:Complemento', 'cfdi:Addenda'
        }
        
        # Remover campos que no son atributos válidos del comprobante
        atributos_filtrados = {k: v for k, v in atributos.items() if k not in campos_a_excluir}
        
        return atributos_filtrados
    
    def _procesar_conceptos(self, datos_json: Dict[str, Any]) -> List[cfdi40.Concepto]:

        seq_conceptos = []
        conceptos_data = None
        
        # Buscar conceptos en diferentes ubicaciones
        if datos_json.get('datosXML', {}).get('cfdi:Comprobante', {}).get('cfdi:Conceptos', {}).get('cfdi:Concepto'):
            conceptos_data = datos_json['datosXML']['cfdi:Comprobante']['cfdi:Conceptos']['cfdi:Concepto']
        elif datos_json.get('datosXML', {}).get('conceptos'):
            conceptos_data = datos_json['datosXML']['conceptos']
        elif datos_json.get('conceptos'):
            conceptos_data = datos_json['conceptos']
        
        if not conceptos_data:
            raise ValueError("No se encontraron conceptos en el JSON")
        
        # Asegurar que conceptos_data sea una lista
        if not isinstance(conceptos_data, list):
            conceptos_data = [conceptos_data]
        
        # Iterar sobre cada concepto
        for idx, concepto_json in enumerate(conceptos_data, 1):
            # ClaveProdServ (campo obligatorio)
            clave_prod = concepto_json.get('ClaveProdServ') or concepto_json.get('clave_prod_serv')
            if not clave_prod:
                raise ValueError(f"ClaveProdServ es obligatorio en el concepto {idx}")
            
            # Cantidad (campo obligatorio) - convertir a decimal
            cantidad_str = concepto_json.get('Cantidad') or concepto_json.get('cantidad')
            if not cantidad_str:
                raise ValueError(f"Cantidad es obligatoria en el concepto {idx}")
            try:
                from decimal import Decimal
                cantidad = Decimal(str(cantidad_str))
            except:
                raise ValueError(f"Cantidad inválida en el concepto {idx}: {cantidad_str}")
            
            # Clave Unidad (campo obligatorio)
            clave_unidad = concepto_json.get('ClaveUnidad') or concepto_json.get('clave_unidad')
            if not clave_unidad:
                raise ValueError(f"ClaveUnidad es obligatoria en el concepto {idx}")
            
            # Descripción (campo obligatorio)
            descripcion = concepto_json.get('Descripcion') or concepto_json.get('descripcion')
            if not descripcion:
                raise ValueError(f"Descripción es obligatoria en el concepto {idx}")
            
            # Valor Unitario (campo obligatorio) - convertir a decimal
            valor_unitario_str = concepto_json.get('ValorUnitario') or concepto_json.get('valor_unitario')
            if not valor_unitario_str:
                raise ValueError(f"ValorUnitario es obligatorio en el concepto {idx}")
            try:
                valor_unitario = Decimal(str(valor_unitario_str))
            except:
                raise ValueError(f"ValorUnitario inválido en el concepto {idx}: {valor_unitario_str}")
            
            # Objeto de Impuesto (campo obligatorio CFDI 4.0)
            objeto_imp = concepto_json.get('ObjetoImp') or concepto_json.get('objeto_imp')
            if not objeto_imp:
                raise ValueError(f"ObjetoImp es obligatorio en el concepto {idx} (CFDI 4.0)")
            
            # Procesar impuestos del concepto (Traslados y Retenciones)
            impuestos_concepto = self._procesar_impuestos_concepto(concepto_json, idx)
            
            # Crear objeto Concepto con los datos extraídos
            # Nota: El importe se calcula automáticamente por satcfdi (cantidad * valor_unitario - descuento)
            # Incluir impuestos en el constructor para que satcfdi los procese correctamente
            renglon = cfdi40.Concepto(
                clave_prod_serv=clave_prod,
                cantidad=cantidad,
                clave_unidad=clave_unidad,
                descripcion=descripcion,
                valor_unitario=valor_unitario,
                objeto_imp=objeto_imp,
                impuestos=impuestos_concepto  # Pasar los impuestos directamente
            )
            
            # Campos opcionales
            no_identificacion = concepto_json.get('NoIdentificacion') or concepto_json.get('no_identificacion')
            if no_identificacion:
                renglon.no_identificacion = no_identificacion
            
            unidad = concepto_json.get('Unidad') or concepto_json.get('unidad')
            if unidad:
                renglon.unidad = unidad
            
            descuento_str = concepto_json.get('Descuento') or concepto_json.get('descuento')
            if descuento_str:
                try:
                    renglon.descuento = Decimal(str(descuento_str))
                except:
                    pass  # Si no se puede convertir, ignorar el descuento
            
            # Agregar el concepto a la lista
            seq_conceptos.append(renglon)
        
        # Validar que haya al menos un concepto
        if len(seq_conceptos) == 0:
            raise ValueError("Debe haber al menos un concepto válido")
        
        return seq_conceptos
    
    def _procesar_impuestos_concepto(self, concepto_json: Dict[str, Any], idx_concepto: int) -> Union[cfdi40.Impuestos, None]:
        """
        Procesa los impuestos (Traslados y Retenciones) de un concepto
        """
        # Buscar impuestos en diferentes ubicaciones
        impuestos_data = (concepto_json.get('cfdi:Impuestos') or 
                         concepto_json.get('Impuestos') or 
                         concepto_json.get('impuestos'))
        
        if not impuestos_data:
            return None
        
        # Procesar Traslados
        traslados = None
        traslados_data = (impuestos_data.get('cfdi:Traslados', {}).get('cfdi:Traslado') or
                         impuestos_data.get('Traslados', {}).get('Traslado') or
                         impuestos_data.get('cfdi:Traslados') or
                         impuestos_data.get('Traslados'))
        
        if traslados_data:
            # Convertir a lista si es un solo traslado
            if isinstance(traslados_data, dict):
                traslados_data = [traslados_data]
            
            traslados_list = []
            for traslado_data in traslados_data:
                traslado_obj = self._crear_traslado_concepto(traslado_data, idx_concepto)
                traslados_list.append(traslado_obj)
            
            traslados = traslados_list if len(traslados_list) > 1 else traslados_list[0]
        
        # Procesar Retenciones
        retenciones = None
        retenciones_data = (impuestos_data.get('cfdi:Retenciones', {}).get('cfdi:Retencion') or
                           impuestos_data.get('Retenciones', {}).get('Retencion') or
                           impuestos_data.get('cfdi:Retenciones') or
                           impuestos_data.get('Retenciones'))
        
        if retenciones_data:
            # Convertir a lista si es una sola retención
            if isinstance(retenciones_data, dict):
                retenciones_data = [retenciones_data]
            
            retenciones_list = []
            for retencion_data in retenciones_data:
                retencion_obj = self._crear_retencion_concepto(retencion_data, idx_concepto)
                retenciones_list.append(retencion_obj)
            
            retenciones = retenciones_list if len(retenciones_list) > 1 else retenciones_list[0]
        
        # Crear objeto Impuestos solo si hay traslados o retenciones
        if traslados or retenciones:
            return cfdi40.Impuestos(
                traslados=traslados,
                retenciones=retenciones
            )
        
        return None
    
    def _crear_traslado_concepto(self, traslado_data: Dict[str, Any], idx_concepto: int) -> cfdi40.Traslado:
        """
        Crea un objeto Traslado desde un diccionario (para conceptos)
        """
        from decimal import Decimal
        
        # Extraer Base (obligatorio)
        base = traslado_data.get('Base') or traslado_data.get('base')
        if base:
            base = Decimal(str(base))
        
        # Extraer Impuesto (obligatorio)
        impuesto = traslado_data.get('Impuesto') or traslado_data.get('impuesto')
        if not impuesto:
            raise ValueError(f"Impuesto es obligatorio en Traslado del concepto {idx_concepto}")
        
        # Extraer TipoFactor (obligatorio)
        tipo_factor = traslado_data.get('TipoFactor') or traslado_data.get('tipo_factor')
        if not tipo_factor:
            raise ValueError(f"TipoFactor es obligatorio en Traslado del concepto {idx_concepto}")
        
        # Extraer TasaOCuota (obligatorio si TipoFactor no es Exento)
        tasa_o_cuota = traslado_data.get('TasaOCuota') or traslado_data.get('tasa_o_cuota')
        if tasa_o_cuota:
            tasa_o_cuota = Decimal(str(tasa_o_cuota))
        
        # Extraer Importe (obligatorio)
        importe = traslado_data.get('Importe') or traslado_data.get('importe')
        if importe:
            importe = Decimal(str(importe))
        
        return cfdi40.Traslado(
            impuesto=impuesto,
            tipo_factor=tipo_factor,
            tasa_o_cuota=tasa_o_cuota,
            importe=importe,
            base=base
        )
    
    def _crear_retencion_concepto(self, retencion_data: Dict[str, Any], idx_concepto: int) -> cfdi40.Retencion:
        """
        Crea un objeto Retencion desde un diccionario (para conceptos)
        """
        from decimal import Decimal
        
        # Extraer Base (obligatorio)
        base = retencion_data.get('Base') or retencion_data.get('base')
        if base:
            base = Decimal(str(base))
        
        # Extraer Impuesto (obligatorio)
        impuesto = retencion_data.get('Impuesto') or retencion_data.get('impuesto')
        if not impuesto:
            raise ValueError(f"Impuesto es obligatorio en Retencion del concepto {idx_concepto}")
        
        # Extraer TipoFactor (obligatorio)
        tipo_factor = retencion_data.get('TipoFactor') or retencion_data.get('tipo_factor')
        if not tipo_factor:
            raise ValueError(f"TipoFactor es obligatorio en Retencion del concepto {idx_concepto}")
        
        # Extraer TasaOCuota (obligatorio si TipoFactor no es Exento)
        tasa_o_cuota = retencion_data.get('TasaOCuota') or retencion_data.get('tasa_o_cuota')
        if tasa_o_cuota:
            tasa_o_cuota = Decimal(str(tasa_o_cuota))
        
        # Extraer Importe (obligatorio)
        importe = retencion_data.get('Importe') or retencion_data.get('importe')
        if importe:
            importe = Decimal(str(importe))
        
        return cfdi40.Retencion(
            impuesto=impuesto,
            tipo_factor=tipo_factor,
            tasa_o_cuota=tasa_o_cuota,
            importe=importe,
            base=base
        )
    
    def _procesar_complementos(self, datos_json: Dict[str, Any]) -> None:
        # Verificar si hay complementos en diferentes ubicaciones posibles
        complemento_data = None
        
        # Buscar en datosXML.cfdi:Comprobante.cfdi:Complemento (nueva estructura)
        if datos_json.get('datosXML', {}).get('cfdi:Comprobante', {}).get('cfdi:Complemento'):
            complemento_data = datos_json['datosXML']['cfdi:Comprobante']['cfdi:Complemento']
        # Buscar en datosXML.complemento (estructura anterior, compatibilidad)
        elif datos_json.get('datosXML', {}).get('complemento'):
            complemento_data = datos_json['datosXML']['complemento']
        
        if complemento_data:
            complementos_list = []
            
            # Carta Porte 3.1 - buscar con prefijo cartaporte31:
            carta_porte_data = complemento_data.get('cartaporte31:CartaPorte') or complemento_data.get('cartaporte31')
            
            if carta_porte_data:
                from .Complementos.cartaPorte import CartaPorteBuilder
                builder = CartaPorteBuilder()
                carta_porte = builder.construir_desde_json(carta_porte_data)
                # Agregar a la lista de complementos
                complementos_list.append(carta_porte)
            
            # Si hay complementos, asignarlos como una LISTA en el diccionario Complemento
            if complementos_list:
                # Asignar como clave del diccionario para que satcfdi lo encuentre
                # satcfdi itera sobre el diccionario Complemento para encontrar complementos
                self.comprobante['Complemento'] = complementos_list if len(complementos_list) > 1 else complementos_list[0]
            
            # Otros complementos pueden agregarse aquí
            # Ejemplo: Terceros, etc.
    
    def _convertir_comprobante_pago(self, datos_json: Dict[str, Any]) -> cfdi40.Comprobante:
        """
        Convierte un JSON a un comprobante de pago CFDI 4.0 con complemento Pago 2.0
        Usa el método especial Comprobante.pago() de satcfdi
        """
        
        # Procesar emisor y receptor
        self.datos_emisor = self._procesar_emisor(datos_json)
        self.datos_receptor = self._procesar_receptor(datos_json)
        
        # Procesar atributos del comprobante
        atributos_comprobante = self._procesar_atributos_comprobante(datos_json)
        lugar_expedicion = atributos_comprobante.pop('lugar_expedicion')
        
        # Procesar el complemento de pago
        complemento_pago = self._procesar_complemento_pago(datos_json)
        
        atributos_validos = {}
        campos_permitidos = ['serie', 'folio', 'fecha', 'confirmacion', 'addenda']
        
        for key in campos_permitidos:
            if key in atributos_comprobante:
                atributos_validos[key] = atributos_comprobante[key]
        
        # Procesar CFDIs relacionados si existen
        self.cfdi_relacionados = self._procesar_cfdi_relacionados(datos_json)
        if self.cfdi_relacionados:
            atributos_validos['cfdi_relacionados'] = self.cfdi_relacionados
        
        self.comprobante = cfdi40.Comprobante.pago(
            emisor=self.datos_emisor,
            receptor=self.datos_receptor,
            lugar_expedicion=lugar_expedicion,
            complemento_pago=complemento_pago,
            **atributos_validos
        )
        
        return self.comprobante
    
    def _procesar_complemento_pago(self, datos_json: Dict[str, Any]) -> 'pago20.Pagos':
        """
        Procesa el complemento de pago 2.0 desde el JSON
        """
        from satcfdi.create.cfd import pago20
        
        # Buscar el complemento de pago en diferentes ubicaciones
        complemento_data = None
        
        # Buscar en datosXML->cfdi:Comprobante->complemento->pago20 (ubicación del cliente)
        if datos_json.get('datosXML', {}).get('cfdi:Comprobante', {}).get('complemento', {}).get('pago20'):
            complemento_data = datos_json['datosXML']['cfdi:Comprobante']['complemento']['pago20']
        # Buscar en datosXML->complemento->pago20 (estructura alternativa)
        elif datos_json.get('datosXML', {}).get('complemento', {}).get('pago20'):
            complemento_data = datos_json['datosXML']['complemento']['pago20']
        # Buscar en datosXML->cfdi:Comprobante->cfdi:Complemento->pago20:Pagos (con prefijos XML)
        elif datos_json.get('datosXML', {}).get('cfdi:Comprobante', {}).get('cfdi:Complemento', {}).get('pago20:Pagos'):
            complemento_data = datos_json['datosXML']['cfdi:Comprobante']['cfdi:Complemento']['pago20:Pagos']
        # Buscar directamente en complemento_pago
        elif datos_json.get('complemento_pago'):
            complemento_data = datos_json['complemento_pago']
        
        if not complemento_data:
            raise ValueError("No se encontró el complemento de pago en el JSON")
        
        # Procesar los pagos
        pagos_data = complemento_data.get('pago20:Pago') or complemento_data.get('Pago') or complemento_data.get('pago') or complemento_data.get('pagos')
        
        if not pagos_data:
            raise ValueError("No se encontraron datos de pagos en el complemento")
        
        # Convertir a lista si es un solo pago
        if isinstance(pagos_data, dict):
            pagos_data = [pagos_data]
        
        # Procesar cada pago
        pagos_list = []
        for pago_data in pagos_data:
            pago_obj = self._crear_objeto_pago(pago_data)
            pagos_list.append(pago_obj)
        
        # Crear objeto Pagos
        # Si hay un solo pago, pasarlo directamente; si hay varios, pasar la lista
        return pago20.Pagos(
            pago=pagos_list if len(pagos_list) > 1 else pagos_list[0]
        )
    
    def _crear_objeto_pago(self, pago_data: Dict[str, Any]) -> 'pago20.Pago':
        """
        Crea un objeto Pago desde un diccionario
        """
        from satcfdi.create.cfd import pago20
        from datetime import datetime
        from decimal import Decimal
        
        # Extraer FechaPago (obligatorio)
        fecha_pago_str = pago_data.get('FechaPago') or pago_data.get('fecha_pago')
        if not fecha_pago_str:
            raise ValueError("FechaPago es obligatorio en el complemento de pago")
        
        # Convertir string a datetime
        if isinstance(fecha_pago_str, str):
            # Intentar diferentes formatos de fecha
            try:
                fecha_pago = datetime.fromisoformat(fecha_pago_str.replace('Z', '+00:00'))
            except:
                try:
                    fecha_pago = datetime.strptime(fecha_pago_str, '%Y-%m-%dT%H:%M:%S')
                except:
                    fecha_pago = datetime.strptime(fecha_pago_str, '%Y-%m-%d')
        else:
            fecha_pago = fecha_pago_str
        
        # Extraer FormaDePagoP (obligatorio)
        forma_pago = pago_data.get('FormaDePagoP') or pago_data.get('forma_de_pago_p')
        if not forma_pago:
            raise ValueError("FormaDePagoP es obligatorio en el pago")
        
        # Extraer MonedaP (obligatorio)
        moneda = pago_data.get('MonedaP') or pago_data.get('moneda_p')
        if not moneda:
            raise ValueError("MonedaP es obligatorio en el pago")
        
        # Extraer TipoCambioP (opcional, pero obligatorio si MonedaP != MXN)
        tipo_cambio = pago_data.get('TipoCambioP') or pago_data.get('tipo_cambio_p')
        if tipo_cambio:
            tipo_cambio = Decimal(str(tipo_cambio))
        
        # Extraer Monto (opcional)
        monto = pago_data.get('Monto') or pago_data.get('monto')
        if monto:
            monto = Decimal(str(monto))
        
        # Procesar documentos relacionados (obligatorio)
        doctos_relacionados = self._procesar_documentos_relacionados(pago_data)
        
        # Construir diccionario de parámetros
        pago_params = {
            'fecha_pago': fecha_pago,
            'forma_de_pago_p': forma_pago,
            'moneda_p': moneda,
            'docto_relacionado': doctos_relacionados
        }
        
        # Agregar parámetros opcionales si existen
        if tipo_cambio:
            pago_params['tipo_cambio_p'] = tipo_cambio
        if monto:
            pago_params['monto'] = monto
        
        # Otros campos opcionales
        campos_opcionales = {
            'NumOperacion': 'num_operacion',
            'RfcEmisorCtaOrd': 'rfc_emisor_cta_ord',
            'NomBancoOrdExt': 'nom_banco_ord_ext',
            'CtaOrdenante': 'cta_ordenante',
            'RfcEmisorCtaBen': 'rfc_emisor_cta_ben',
            'CtaBeneficiario': 'cta_beneficiario',
            'TipoCadPago': 'tipo_cad_pago',
            'CertPago': 'cert_pago',
            'CadPago': 'cad_pago',
            'SelloPago': 'sello_pago'
        }
        
        for campo_json, campo_python in campos_opcionales.items():
            valor = pago_data.get(campo_json) or pago_data.get(campo_python)
            if valor:
                pago_params[campo_python] = valor
        
        return pago20.Pago(**pago_params)
    
    def _procesar_documentos_relacionados(self, pago_data: Dict[str, Any]) -> Union['pago20.DoctoRelacionado', List['pago20.DoctoRelacionado']]:
        """
        Procesa los documentos relacionados de un pago
        """
        
        # Buscar documentos relacionados
        doctos_data = (pago_data.get('pago20:DoctoRelacionado') or 
                      pago_data.get('DoctoRelacionado') or 
                      pago_data.get('docto_relacionado') or
                      pago_data.get('documentos_relacionados'))
        
        if not doctos_data:
            raise ValueError("Se requiere al menos un documento relacionado en el pago")
        
        # Convertir a lista si es un solo documento
        if isinstance(doctos_data, dict):
            doctos_data = [doctos_data]
        
        # Procesar cada documento
        doctos_list = []
        for docto_data in doctos_data:
            docto_obj = self._crear_documento_relacionado(docto_data)
            doctos_list.append(docto_obj)
        
        # Si hay un solo documento, retornarlo directamente; si hay varios, retornar la lista
        return doctos_list if len(doctos_list) > 1 else doctos_list[0]
    
    def _crear_documento_relacionado(self, docto_data: Dict[str, Any]) -> 'pago20.DoctoRelacionado':
        """
        Crea un objeto DoctoRelacionado desde un diccionario
        """
        from satcfdi.create.cfd import pago20
        from decimal import Decimal
        
        # Extraer IdDocumento (UUID - obligatorio)
        id_documento = docto_data.get('IdDocumento') or docto_data.get('id_documento')
        if not id_documento:
            raise ValueError("IdDocumento (UUID) es obligatorio en el documento relacionado")
        
        # Extraer ImpPagado (obligatorio)
        imp_pagado = docto_data.get('ImpPagado') or docto_data.get('imp_pagado')
        if imp_pagado is None:
            raise ValueError("ImpPagado es obligatorio en el documento relacionado")
        imp_pagado = Decimal(str(imp_pagado))
        
        # Extraer ImpSaldoAnt (obligatorio)
        imp_saldo_ant = docto_data.get('ImpSaldoAnt') or docto_data.get('imp_saldo_ant')
        if imp_saldo_ant is None:
            raise ValueError("ImpSaldoAnt es obligatorio en el documento relacionado")
        imp_saldo_ant = Decimal(str(imp_saldo_ant))
        
        # Extraer ObjetoImpDR (obligatorio en CFDI 4.0)
        objeto_imp_dr = docto_data.get('ObjetoImpDR') or docto_data.get('objeto_imp_dr')
        if not objeto_imp_dr:
            raise ValueError("ObjetoImpDR es obligatorio en el documento relacionado")
        
        # Extraer MonedaDR (obligatorio)
        moneda_dr = docto_data.get('MonedaDR') or docto_data.get('moneda_dr')
        if not moneda_dr:
            raise ValueError("MonedaDR es obligatorio en el documento relacionado")
        
        # Construir parámetros base
        docto_params = {
            'id_documento': id_documento,
            'imp_pagado': imp_pagado,
            'imp_saldo_ant': imp_saldo_ant,
            'objeto_imp_dr': objeto_imp_dr,
            'moneda_dr': moneda_dr
        }
        
        # Campos opcionales según la firma de DoctoRelacionado de satcfdi
        campos_opcionales = {
            'Serie': 'serie',
            'Folio': 'folio',
            'NumParcialidad': 'num_parcialidad',
            'EquivalenciaDR': 'equivalencia_dr'
        }
        
        for campo_json, campo_python in campos_opcionales.items():
            valor = docto_data.get(campo_json) or docto_data.get(campo_python)
            if valor is not None:
                # Convertir valores numéricos a Decimal si es necesario
                if campo_python == 'equivalencia_dr':
                    valor = Decimal(str(valor))
                elif campo_python == 'num_parcialidad':
                    valor = int(valor)
                docto_params[campo_python] = valor
        
        # Procesar ImpuestosDR si existe
        impuestos_dr = self._procesar_impuestos_dr(docto_data)
        if impuestos_dr:
            docto_params['impuestos_dr'] = impuestos_dr
        
        return pago20.DoctoRelacionado(**docto_params)
    
    def _procesar_impuestos_dr(self, docto_data: Dict[str, Any]) -> Union['pago20.ImpuestosDR', None]:
        """
        Procesa los impuestos relacionados de un documento relacionado
        """
        from satcfdi.create.cfd import pago20
        
        impuestos_data = docto_data.get('ImpuestosDR') or docto_data.get('impuestos_dr')
        if not impuestos_data:
            return None
        
        # Procesar TrasladosDR
        traslados_dr = None
        if 'TrasladosDR' in impuestos_data:
            traslados_data = impuestos_data['TrasladosDR']
            if isinstance(traslados_data, dict):
                traslados_data = [traslados_data]
            traslados_list = []
            for traslado_data in traslados_data:
                traslado_obj = self._crear_traslado_dr(traslado_data)
                traslados_list.append(traslado_obj)
            traslados_dr = traslados_list if len(traslados_list) > 1 else traslados_list[0]
        
        # Procesar RetencionesDR (si existe)
        retenciones_dr = None
        if 'RetencionesDR' in impuestos_data:
            retenciones_data = impuestos_data['RetencionesDR']
            if isinstance(retenciones_data, dict):
                retenciones_data = [retenciones_data]
            retenciones_list = []
            for retencion_data in retenciones_data:
                retencion_obj = self._crear_retencion_dr(retencion_data)
                retenciones_list.append(retencion_obj)
            retenciones_dr = retenciones_list if len(retenciones_list) > 1 else retenciones_list[0]
        
        # Crear ImpuestosDR
        if traslados_dr or retenciones_dr:
            return pago20.ImpuestosDR(
                traslados_dr=traslados_dr,
                retenciones_dr=retenciones_dr
            )
        return None
    
    def _crear_traslado_dr(self, traslado_data: Dict[str, Any]) -> 'pago20.TrasladoDR':
        """
        Crea un objeto TrasladoDR desde un diccionario
        """
        from satcfdi.create.cfd import pago20
        from decimal import Decimal
        
        base_dr = Decimal(str(traslado_data.get('BaseDR', 0)))
        impuesto_dr = traslado_data.get('ImpuestoDR')
        tipo_factor_dr = traslado_data.get('TipoFactorDR')
        tasa_o_cuota_dr = Decimal(str(traslado_data.get('TasaOCuotaDR', 0)))
        importe_dr = Decimal(str(traslado_data.get('ImporteDR', 0)))
        
        return pago20.TrasladoDR(
            base_dr=base_dr,
            impuesto_dr=impuesto_dr,
            tipo_factor_dr=tipo_factor_dr,
            tasa_o_cuota_dr=tasa_o_cuota_dr,
            importe_dr=importe_dr
        )
    
    def _crear_retencion_dr(self, retencion_data: Dict[str, Any]) -> 'pago20.RetencionDR':
        """
        Crea un objeto RetencionDR desde un diccionario
        """
        from satcfdi.create.cfd import pago20
        from decimal import Decimal
        
        base_dr = Decimal(str(retencion_data.get('BaseDR', 0)))
        impuesto_dr = retencion_data.get('ImpuestoDR')
        tipo_factor_dr = retencion_data.get('TipoFactorDR')
        tasa_o_cuota_dr = Decimal(str(retencion_data.get('TasaOCuotaDR', 0)))
        importe_dr = Decimal(str(retencion_data.get('ImporteDR', 0)))
        
        return pago20.RetencionDR(
            base_dr=base_dr,
            impuesto_dr=impuesto_dr,
            tipo_factor_dr=tipo_factor_dr,
            tasa_o_cuota_dr=tasa_o_cuota_dr,
            importe_dr=importe_dr
        )
    
    @staticmethod
    def validar_estructura_json(datos_json: Dict[str, Any]) -> bool:
        """
        Valida que el JSON tenga la estructura mínima requerida.
        Soporta múltiples formatos de JSON (estructura plana o con datosXML).
        """
        if not isinstance(datos_json, dict):
            raise ValueError("El JSON debe ser un diccionario")
        
        # Verificar si existe la estructura datosXML
        if 'datosXML' in datos_json:
            # Validar estructura con namespace cfdi:
            if 'cfdi:Comprobante' in datos_json['datosXML']:
                comprobante = datos_json['datosXML']['cfdi:Comprobante']
                
                # Validar emisor
                if 'cfdi:Emisor' not in comprobante:
                    raise ValueError("Falta la sección 'cfdi:Emisor' en datosXML->cfdi:Comprobante")
                
                # Validar receptor
                if 'cfdi:Receptor' not in comprobante:
                    raise ValueError("Falta la sección 'cfdi:Receptor' en datosXML->cfdi:Comprobante")
                
                # Validar conceptos
                if 'cfdi:Conceptos' not in comprobante:
                    raise ValueError("Falta la sección 'cfdi:Conceptos' en datosXML->cfdi:Comprobante")
                
                return True
            # Validar estructura sin namespace
            elif 'emisor' in datos_json['datosXML'] or 'receptor' in datos_json['datosXML']:
                if 'emisor' not in datos_json['datosXML']:
                    raise ValueError("Falta la sección 'emisor' en datosXML")
                if 'receptor' not in datos_json['datosXML']:
                    raise ValueError("Falta la sección 'receptor' en datosXML")
                return True
        
        # Validar estructura plana (sin datosXML)
        if 'emisor' not in datos_json:
            raise ValueError("Falta la sección 'emisor' en el JSON")
        
        if 'receptor' not in datos_json:
            raise ValueError("Falta la sección 'receptor' en el JSON")
        
        if 'conceptos' not in datos_json:
            raise ValueError("Falta la sección 'conceptos' en el JSON")
        
        return True