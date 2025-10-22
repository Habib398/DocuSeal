from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict, Any
from satcfdi.cfdi import CFDI
from satcfdi.create.cfd import cartaporte31


class CartaPorteBuilder:
    
    def construir_desde_json(self, carta_porte_data: Dict[str, Any]) -> cartaporte31.CartaPorte:
        """
        Construye un objeto CartaPorte desde datos JSON.
        """
        try:
            # Atributos principales de CartaPorte (obligatorios)
            transp_internac = carta_porte_data.get('TranspInternac') or carta_porte_data.get('transp_internac')
            if not transp_internac:
                raise ValueError("TranspInternac es obligatorio en CartaPorte")
            
            total_dist_rec = carta_porte_data.get('TotalDistRec') or carta_porte_data.get('total_dist_rec')
            if total_dist_rec:
                total_dist_rec = Decimal(str(total_dist_rec))
            
            # Procesar Ubicaciones (obligatorio)
            ubicaciones = self._procesar_ubicaciones(carta_porte_data)
            
            # Procesar Mercancias (obligatorio)
            mercancias = self._procesar_mercancias(carta_porte_data)
            
            # Crear objeto CartaPorte
            carta_porte = cartaporte31.CartaPorte(
                transp_internac=transp_internac,
                ubicaciones=ubicaciones,
                mercancias=mercancias
            )
            
            # Agregar atributos opcionales
            if total_dist_rec:
                carta_porte.total_dist_rec = total_dist_rec
            
            # Procesar FiguraTransporte (opcional)
            if carta_porte_data.get('FiguraTransporte') or carta_porte_data.get('figura_transporte'):
                figura_transporte = self._procesar_figura_transporte(carta_porte_data)
                if figura_transporte:
                    carta_porte.figura_transporte = figura_transporte
            
            return carta_porte
            
        except Exception as e:
            raise ValueError(f"Error al procesar CartaPorte: {str(e)}")
    
    def _procesar_ubicaciones(self, carta_porte_data: Dict[str, Any]) -> List[cartaporte31.Ubicacion]:
        """
        Procesa la lista de ubicaciones de Carta Porte.
        """
        ubicaciones_data = (carta_porte_data.get('Ubicaciones', {}).get('Ubicacion') or
                           carta_porte_data.get('ubicaciones', {}).get('ubicacion') or
                           carta_porte_data.get('ubicaciones'))
        
        if not ubicaciones_data:
            raise ValueError("Ubicaciones es obligatorio en CartaPorte")
        
        # Asegurar que sea una lista
        if not isinstance(ubicaciones_data, list):
            ubicaciones_data = [ubicaciones_data]
        
        ubicaciones = []
        for idx, ub_data in enumerate(ubicaciones_data, 1):
            # Campos obligatorios
            tipo_ubicacion = ub_data.get('TipoUbicacion') or ub_data.get('tipo_ubicacion')
            if not tipo_ubicacion:
                raise ValueError(f"TipoUbicacion es obligatorio en Ubicacion {idx}")
            
            # Crear objeto Ubicacion
            ubicacion = cartaporte31.Ubicacion(
                tipo_ubicacion=tipo_ubicacion
            )
            
            # Campos condicionales según el tipo
            id_ubicacion = ub_data.get('IDUbicacion') or ub_data.get('id_ubicacion')
            if id_ubicacion:
                ubicacion.id_ubicacion = id_ubicacion
            
            rfc_remitente_destinatario = (ub_data.get('RFCRemitenteDestinatario') or 
                                         ub_data.get('rfc_remitente_destinatario'))
            if rfc_remitente_destinatario:
                ubicacion.rfc_remitente_destinatario = rfc_remitente_destinatario
            
            nombre_remitente_destinatario = (ub_data.get('NombreRemitenteDestinatario') or 
                                            ub_data.get('nombre_remitente_destinatario'))
            if nombre_remitente_destinatario:
                ubicacion.nombre_remitente_destinatario = nombre_remitente_destinatario
            
            fecha_hora_salida_llegada = (ub_data.get('FechaHoraSalidaLlegada') or 
                                        ub_data.get('fecha_hora_salida_llegada'))
            if fecha_hora_salida_llegada:
                if isinstance(fecha_hora_salida_llegada, str):
                    try:
                        ubicacion.fecha_hora_salida_llegada = datetime.fromisoformat(fecha_hora_salida_llegada)
                    except ValueError:
                        ubicacion.fecha_hora_salida_llegada = datetime.strptime(fecha_hora_salida_llegada, '%Y-%m-%d %H:%M:%S')
                else:
                    ubicacion.fecha_hora_salida_llegada = fecha_hora_salida_llegada
            
            distancia_recorrida = ub_data.get('DistanciaRecorrida') or ub_data.get('distancia_recorrida')
            if distancia_recorrida:
                ubicacion.distancia_recorrida = Decimal(str(distancia_recorrida))
            
            # Procesar Domicilio
            if ub_data.get('Domicilio') or ub_data.get('domicilio'):
                domicilio_data = ub_data.get('Domicilio') or ub_data.get('domicilio')
                domicilio = self._procesar_domicilio(domicilio_data)
                ubicacion.domicilio = domicilio
            
            ubicaciones.append(ubicacion)
        
        if len(ubicaciones) < 2:
            raise ValueError("Debe haber al menos 2 ubicaciones en CartaPorte (origen y destino)")
        
        return ubicaciones
    
    def _procesar_domicilio(self, domicilio_data: Dict[str, Any]) -> cartaporte31.Domicilio:
        """
        Procesa los datos del domicilio de una ubicación.
        """
        # Campos obligatorios
        pais = domicilio_data.get('Pais') or domicilio_data.get('pais')
        if not pais:
            raise ValueError("Pais es obligatorio en Domicilio")
        
        domicilio = cartaporte31.Domicilio(pais=pais)
        
        # Campos opcionales/condicionales
        calle = domicilio_data.get('Calle') or domicilio_data.get('calle')
        if calle:
            domicilio.calle = calle
        
        numero_exterior = domicilio_data.get('NumeroExterior') or domicilio_data.get('numero_exterior')
        if numero_exterior:
            domicilio.numero_exterior = numero_exterior
        
        numero_interior = domicilio_data.get('NumeroInterior') or domicilio_data.get('numero_interior')
        if numero_interior:
            domicilio.numero_interior = numero_interior
        
        colonia = domicilio_data.get('Colonia') or domicilio_data.get('colonia')
        if colonia:
            domicilio.colonia = colonia
        
        localidad = domicilio_data.get('Localidad') or domicilio_data.get('localidad')
        if localidad:
            domicilio.localidad = localidad
        
        referencia = domicilio_data.get('Referencia') or domicilio_data.get('referencia')
        if referencia:
            domicilio.referencia = referencia
        
        municipio = domicilio_data.get('Municipio') or domicilio_data.get('municipio')
        if municipio:
            domicilio.municipio = municipio
        
        estado = domicilio_data.get('Estado') or domicilio_data.get('estado')
        if estado:
            domicilio.estado = estado
        
        codigo_postal = domicilio_data.get('CodigoPostal') or domicilio_data.get('codigo_postal')
        if codigo_postal:
            domicilio.codigo_postal = codigo_postal
        
        return domicilio
    
    def _procesar_mercancias(self, carta_porte_data: Dict[str, Any]) -> cartaporte31.Mercancias:
        """
        Procesa la sección de Mercancías de Carta Porte.
        """
        mercancias_data = (carta_porte_data.get('Mercancias') or 
                          carta_porte_data.get('mercancias'))
        
        if not mercancias_data:
            raise ValueError("Mercancias es obligatorio en CartaPorte")
        
        # Campos obligatorios
        peso_bruto_total = (mercancias_data.get('PesoBrutoTotal') or 
                           mercancias_data.get('peso_bruto_total'))
        if not peso_bruto_total:
            raise ValueError("PesoBrutoTotal es obligatorio en Mercancias")
        
        unidad_peso = mercancias_data.get('UnidadPeso') or mercancias_data.get('unidad_peso')
        if not unidad_peso:
            raise ValueError("UnidadPeso es obligatorio en Mercancias")
        
        # Procesar lista de Mercancia
        mercancia_list = self._procesar_lista_mercancias(mercancias_data)
        
        # Crear objeto Mercancias
        mercancias = cartaporte31.Mercancias(
            peso_bruto_total=Decimal(str(peso_bruto_total)),
            unidad_peso=unidad_peso,
            mercancia=mercancia_list
        )
        
        # Campos opcionales
        num_total_mercancias = (mercancias_data.get('NumTotalMercancias') or 
                               mercancias_data.get('num_total_mercancias'))
        if num_total_mercancias:
            mercancias.num_total_mercancias = int(num_total_mercancias)
        
        # Procesar tipo de transporte (switch-like logic)
        tipo_transporte = mercancias_data.get('TipoTransporte') or mercancias_data.get('tipo_transporte')
        if tipo_transporte == 'Autotransporte' or mercancias_data.get('Autotransporte') or mercancias_data.get('autotransporte'):
            autotransporte = self._procesar_autotransporte(mercancias_data)
            if autotransporte:
                mercancias.autotransporte = autotransporte
        elif tipo_transporte == 'Aereo':
            transporte_aereo = self._procesar_transporte_aereo(mercancias_data)
            if transporte_aereo:
                mercancias.transporte_aereo = transporte_aereo  # Asumiendo que la clase Mercancias lo soporta
        elif tipo_transporte == 'Maritimo':
            transporte_maritimo = self._procesar_transporte_maritimo(mercancias_data)
            if transporte_maritimo:
                mercancias.transporte_maritimo = transporte_maritimo
        elif tipo_transporte == 'Ferroviario':
            transporte_ferroviario = self._procesar_transporte_ferroviario(mercancias_data)
            if transporte_ferroviario:
                mercancias.transporte_ferroviario = transporte_ferroviario
        # Agregar más elif para otros tipos en el futuro
        
        return mercancias
    
    def _procesar_lista_mercancias(self, mercancias_data: Dict[str, Any]) -> List[cartaporte31.Mercancia]:
        """
        Procesa la lista individual de mercancías.
        """
        mercancia_list_data = (mercancias_data.get('Mercancia') or 
                              mercancias_data.get('mercancia'))
        
        if not mercancia_list_data:
            raise ValueError("Debe haber al menos una Mercancia")
        
        # Asegurar que sea una lista
        if not isinstance(mercancia_list_data, list):
            mercancia_list_data = [mercancia_list_data]
        
        mercancia_list = []
        for idx, merc_data in enumerate(mercancia_list_data, 1):
            # Campos obligatorios
            bienh_transp = merc_data.get('BienesTransp') or merc_data.get('bienes_transp')
            if not bienh_transp:
                raise ValueError(f"BienesTransp es obligatorio en Mercancia {idx}")
            
            descripcion = merc_data.get('Descripcion') or merc_data.get('descripcion')
            if not descripcion:
                raise ValueError(f"Descripcion es obligatorio en Mercancia {idx}")
            
            cantidad = merc_data.get('Cantidad') or merc_data.get('cantidad')
            if not cantidad:
                raise ValueError(f"Cantidad es obligatorio en Mercancia {idx}")
            
            clave_unidad = merc_data.get('ClaveUnidad') or merc_data.get('clave_unidad')
            if not clave_unidad:
                raise ValueError(f"ClaveUnidad es obligatorio en Mercancia {idx}")
            
            peso_en_kg = merc_data.get('PesoEnKg') or merc_data.get('peso_en_kg')
            if not peso_en_kg:
                raise ValueError(f"PesoEnKg es obligatorio en Mercancia {idx}")
            
            # Crear objeto Mercancia
            mercancia = cartaporte31.Mercancia(
                bienes_transp=bienh_transp,
                descripcion=descripcion,
                cantidad=Decimal(str(cantidad)),
                clave_unidad=clave_unidad,
                peso_en_kg=Decimal(str(peso_en_kg))
            )
            
            # Campos opcionales
            unidad = merc_data.get('Unidad') or merc_data.get('unidad')
            if unidad:
                mercancia.unidad = unidad
            
            valor_mercancia = merc_data.get('ValorMercancia') or merc_data.get('valor_mercancia')
            if valor_mercancia:
                mercancia.valor_mercancia = Decimal(str(valor_mercancia))
            
            moneda = merc_data.get('Moneda') or merc_data.get('moneda')
            if moneda:
                mercancia.moneda = moneda
            
            fraccion_arancelaria = (merc_data.get('FraccionArancelaria') or 
                                   merc_data.get('fraccion_arancelaria'))
            if fraccion_arancelaria:
                mercancia.fraccion_arancelaria = fraccion_arancelaria
            
            uuid_comercio_ext = merc_data.get('UUIDComercioExt') or merc_data.get('uuid_comercio_ext')
            if uuid_comercio_ext:
                mercancia.uuid_comercio_ext = uuid_comercio_ext
            
            mercancia_list.append(mercancia)
        
        return mercancia_list
    
    def _procesar_autotransporte(self, mercancias_data: Dict[str, Any]) -> Optional[cartaporte31.Autotransporte]:
        """
        Procesa la sección de Autotransporte.
        """
        autotransporte_data = (mercancias_data.get('Autotransporte') or 
                              mercancias_data.get('autotransporte'))
        
        if not autotransporte_data:
            return None
        
        # Campos obligatorios
        perm_sct = autotransporte_data.get('PermSCT') or autotransporte_data.get('perm_sct')
        if not perm_sct:
            raise ValueError("PermSCT es obligatorio en Autotransporte")
        
        num_permiso_sct = (autotransporte_data.get('NumPermisoSCT') or 
                          autotransporte_data.get('num_permiso_sct'))
        if not num_permiso_sct:
            raise ValueError("NumPermisoSCT es obligatorio en Autotransporte")
        
        # Crear objeto Autotransporte
        autotransporte = cartaporte31.Autotransporte(
            perm_sct=perm_sct,
            num_permiso_sct=num_permiso_sct
        )
        
        # Procesar IdentificacionVehicular (condicional)
        if autotransporte_data.get('IdentificacionVehicular') or autotransporte_data.get('identificacion_vehicular'):
            id_vehicular_data = (autotransporte_data.get('IdentificacionVehicular') or 
                                autotransporte_data.get('identificacion_vehicular'))
            id_vehicular = self._procesar_identificacion_vehicular(id_vehicular_data)
            if id_vehicular:
                autotransporte.identificacion_vehicular = id_vehicular
        
        # Procesar Seguros (condicional)
        if autotransporte_data.get('Seguros') or autotransporte_data.get('seguros'):
            seguros_data = autotransporte_data.get('Seguros') or autotransporte_data.get('seguros')
            seguros = self._procesar_seguros(seguros_data)
            if seguros:
                autotransporte.seguros = seguros
        
        # Procesar Remolques (opcional)
        if autotransporte_data.get('Remolques') or autotransporte_data.get('remolques'):
            remolques_data = autotransporte_data.get('Remolques') or autotransporte_data.get('remolques')
            remolques = self._procesar_remolques(remolques_data)
            if remolques:
                autotransporte.remolques = remolques
        
        return autotransporte
    
    def _procesar_transporte_aereo(self, mercancias_data: Dict[str, Any]) -> Optional[Any]:
        # Aquí va la lógica de transporte aéreo
        raise NotImplementedError("Transporte Aereo no implementado aún")
    
    def _procesar_transporte_maritimo(self, mercancias_data: Dict[str, Any]) -> Optional[Any]:
        # Aquí va la lógica de transporte marítimo
        raise NotImplementedError("Transporte Maritimo no implementado aún")
    
    def _procesar_transporte_ferroviario(self, mercancias_data: Dict[str, Any]) -> Optional[Any]:
        # Aquí va la lógica de transporte ferroviario
        raise NotImplementedError("Transporte Ferroviario no implementado aún")
    
    def _procesar_identificacion_vehicular(self, id_vehicular_data: Dict[str, Any]) -> cartaporte31.IdentificacionVehicular:
        """
        Procesa los datos de IdentificacionVehicular.
        """
        # Campos obligatorios
        config_vehicular = (id_vehicular_data.get('ConfigVehicular') or 
                           id_vehicular_data.get('config_vehicular'))
        if not config_vehicular:
            raise ValueError("ConfigVehicular es obligatorio en IdentificacionVehicular")
        
        placa_vm = id_vehicular_data.get('PlacaVM') or id_vehicular_data.get('placa_vm')
        if not placa_vm:
            raise ValueError("PlacaVM es obligatorio en IdentificacionVehicular")
        
        anio_modelo_vm = id_vehicular_data.get('AnioModeloVM') or id_vehicular_data.get('anio_modelo_vm')
        if not anio_modelo_vm:
            raise ValueError("AnioModeloVM es obligatorio en IdentificacionVehicular")
        
        # Crear objeto IdentificacionVehicular
        id_vehicular = cartaporte31.IdentificacionVehicular(
            config_vehicular=config_vehicular,
            placa_vm=placa_vm,
            anio_modelo_vm=int(anio_modelo_vm)
        )
        
        return id_vehicular
    
    def _procesar_seguros(self, seguros_data: Dict[str, Any]) -> cartaporte31.Seguros:
        """
        Procesa los datos de Seguros del Autotransporte.
        """
        # Campos obligatorios
        asegura_resp_civil = (seguros_data.get('AseguraRespCivil') or 
                             seguros_data.get('asegura_resp_civil'))
        if not asegura_resp_civil:
            raise ValueError("AseguraRespCivil es obligatorio en Seguros")
        
        poliza_resp_civil = (seguros_data.get('PolizaRespCivil') or 
                            seguros_data.get('poliza_resp_civil'))
        if not poliza_resp_civil:
            raise ValueError("PolizaRespCivil es obligatorio en Seguros")
        
        # Crear objeto Seguros
        seguros = cartaporte31.Seguros(
            asegura_resp_civil=asegura_resp_civil,
            poliza_resp_civil=poliza_resp_civil
        )
        
        # Campos opcionales
        asegura_med_ambiente = (seguros_data.get('AseguraMedAmbiente') or 
                               seguros_data.get('asegura_med_ambiente'))
        if asegura_med_ambiente:
            seguros.asegura_med_ambiente = asegura_med_ambiente
        
        poliza_med_ambiente = (seguros_data.get('PolizaMedAmbiente') or 
                              seguros_data.get('poliza_med_ambiente'))
        if poliza_med_ambiente:
            seguros.poliza_med_ambiente = poliza_med_ambiente
        
        asegura_carga = seguros_data.get('AseguraCarga') or seguros_data.get('asegura_carga')
        if asegura_carga:
            seguros.asegura_carga = asegura_carga
        
        poliza_carga = seguros_data.get('PolizaCarga') or seguros_data.get('poliza_carga')
        if poliza_carga:
            seguros.poliza_carga = poliza_carga
        
        prima_seguro = seguros_data.get('PrimaSeguro') or seguros_data.get('prima_seguro')
        if prima_seguro:
            seguros.prima_seguro = Decimal(str(prima_seguro))
        
        return seguros
    
    def _procesar_remolques(self, remolques_data: Dict[str, Any]) -> List[cartaporte31.Remolque]:
        """
        Procesa la lista de remolques del Autotransporte.
        """
        remolque_list_data = remolques_data.get('Remolque') or remolques_data.get('remolque')
        
        if not remolque_list_data:
            return []
        
        # Asegurar que sea una lista
        if not isinstance(remolque_list_data, list):
            remolque_list_data = [remolque_list_data]
        
        remolques = []
        for idx, remolque_data in enumerate(remolque_list_data, 1):
            # Campos obligatorios
            sub_tipo_rem = remolque_data.get('SubTipoRem') or remolque_data.get('sub_tipo_rem')
            if not sub_tipo_rem:
                raise ValueError(f"SubTipoRem es obligatorio en Remolque {idx}")
            
            placa = remolque_data.get('Placa') or remolque_data.get('placa')
            if not placa:
                raise ValueError(f"Placa es obligatorio en Remolque {idx}")
            
            # Crear objeto Remolque
            remolque = cartaporte31.Remolque(
                sub_tipo_rem=sub_tipo_rem,
                placa=placa
            )
            
            remolques.append(remolque)
        
        return remolques
    
    def _procesar_figura_transporte(self, carta_porte_data: Dict[str, Any]) -> Optional[List[cartaporte31.TiposFigura]]:
        """
        Procesa la sección de FiguraTransporte.
        """
        figura_data = (carta_porte_data.get('FiguraTransporte') or 
                      carta_porte_data.get('figura_transporte'))
        
        if not figura_data:
            return None
        
        tipos_figura_data = figura_data.get('TiposFigura') or figura_data.get('tipos_figura')
        
        if not tipos_figura_data:
            return None
        
        # Asegurar que sea una lista
        if not isinstance(tipos_figura_data, list):
            tipos_figura_data = [tipos_figura_data]
        
        tipos_figura_list = []
        for idx, tipo_data in enumerate(tipos_figura_data, 1):
            # Campos obligatorios
            tipo_figura = tipo_data.get('TipoFigura') or tipo_data.get('tipo_figura')
            if not tipo_figura:
                raise ValueError(f"TipoFigura es obligatorio en TiposFigura {idx}")
            
            rfc_figura = tipo_data.get('RFCFigura') or tipo_data.get('rfc_figura')
            if not rfc_figura:
                raise ValueError(f"RFCFigura es obligatorio en TiposFigura {idx}")
            
            nombre_figura = tipo_data.get('NombreFigura') or tipo_data.get('nombre_figura')
            if not nombre_figura:
                raise ValueError(f"NombreFigura es obligatorio en TiposFigura {idx}")
            
            # Crear objeto TiposFigura
            tipo_figura_obj = cartaporte31.TiposFigura(
                tipo_figura=tipo_figura,
                rfc_figura=rfc_figura,
                nombre_figura=nombre_figura
            )
            
            # Campos opcionales
            num_licencia = tipo_data.get('NumLicencia') or tipo_data.get('num_licencia')
            if num_licencia:
                tipo_figura_obj.num_licencia = num_licencia
            
            tipos_figura_list.append(tipo_figura_obj)
        
        return tipos_figura_list if tipos_figura_list else None


class CartaPorteExtractor:
    def __init__(self, cfdi: CFDI):
        self.cfdi = cfdi

    def extraer_carta_porte(self) -> Optional[cartaporte31.CartaPorte]:
        """
        Extrae el complemento CartaPorte del CFDI si existe.
        Retorna el objeto CartaPorte o None si no hay complemento.
        """
        complemento = self.cfdi.get('Complemento')
        if not complemento:
            return None
        
        carta_porte_data = complemento.get('CartaPorte')
        if not carta_porte_data:
            return None
        
        # objeto carta porte
        if isinstance(carta_porte_data, cartaporte31.CartaPorte):
            return carta_porte_data
        return None

    def obtener_datos_carta_porte(self) -> Optional[Dict[str, Any]]:
        """
        Retorna los datos del complemento CartaPorte como un dict para facilitar el acceso.
        """
        carta_porte = self.extraer_carta_porte()
        if not carta_porte:
            return None
        
        # Acceder a atributos del objeto CartaPorte
        return {
            'version': getattr(carta_porte, 'version', None),
            'id_ccp': getattr(carta_porte, 'id_ccp', None),
            'transp_internac': getattr(carta_porte, 'transp_internac', None),
            'total_dist_rec': getattr(carta_porte, 'total_dist_rec', None),
            'ubicaciones': getattr(carta_porte, 'ubicaciones', []),
            'mercancias': getattr(carta_porte, 'mercancias', None)
        }