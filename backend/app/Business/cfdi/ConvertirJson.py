from satcfdi.create.cfd import cfdi40
from typing import Dict, Any, List


class ConvertirJson:
    
    def __init__(self):
        self.comprobante = None
        self.datos_emisor = None
        self.datos_receptor = None
        self.conceptos = []
    
    def convertir_a_cfdi(self, datos_json: Dict[str, Any]) -> cfdi40.Comprobante:
        self.datos_emisor = self._procesar_emisor(datos_json)
        self.datos_receptor = self._procesar_receptor(datos_json)
        self.conceptos = self._procesar_conceptos(datos_json)
        atributos_comprobante = self._procesar_atributos_comprobante(datos_json)
        
        # Extraer y eliminar lugar_expedicion del diccionario para pasarlo como argumento
        lugar_expedicion = atributos_comprobante.pop('lugar_expedicion')
        self.comprobante = cfdi40.Comprobante(
            emisor=self.datos_emisor,
            lugar_expedicion=lugar_expedicion,
            receptor=self.datos_receptor,
            conceptos=self.conceptos,
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
    
    def _procesar_atributos_comprobante(self, datos_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa los atributos principales del comprobante desde el JSON.
        Extrae los datos desde datosXML->cfdi:Comprobante o estructura plana.
        Retorna un diccionario con los atributos para crear el Comprobante.
        
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
            
            # Crear objeto Concepto con los datos extraídos
            # Nota: El importe se calcula automáticamente por satcfdi (cantidad * valor_unitario - descuento)
            renglon = cfdi40.Concepto(
                clave_prod_serv=clave_prod,
                cantidad=cantidad,
                clave_unidad=clave_unidad,
                descripcion=descripcion,
                valor_unitario=valor_unitario,
                objeto_imp=objeto_imp
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
    
    def _procesar_complementos(self, datos_json: Dict[str, Any]) -> None:
        # Verificar si hay complementos
        if datos_json.get('datosXML', {}).get('complemento'):
            complemento_data = datos_json['datosXML']['complemento']
            
            # Carta Porte 3.1
            if complemento_data.get('cartaporte31'):
                from .Complementos.cartaPorte import CartaPorteBuilder
                builder = CartaPorteBuilder()
                carta_porte = builder.construir_desde_json(complemento_data['cartaporte31'])
                
                # Agregar el complemento al comprobante
                if not hasattr(self.comprobante, 'complemento') or self.comprobante.complemento is None:
                    from satcfdi.create.cfd import cartaporte31
                    self.comprobante.complemento = cartaporte31.Complemento()
                
                self.comprobante.complemento.carta_porte = carta_porte
            
            # Otros complementos pueden agregarse aquí
            # Ejemplo: Pago 2.0, Terceros, etc.
    
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