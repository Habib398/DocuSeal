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
            
            id_ccp = carta_porte_data.get('IdCCP') or carta_porte_data.get('id_ccp')
            if not id_ccp:
                raise ValueError("IdCCP es obligatorio en CartaPorte")
            
            total_dist_rec = carta_porte_data.get('TotalDistRec') or carta_porte_data.get('total_dist_rec')
            if total_dist_rec:
                total_dist_rec = Decimal(str(total_dist_rec))
            
            # Procesar Ubicaciones (obligatorio)
            ubicaciones = self._procesar_ubicaciones(carta_porte_data)
            
            # Procesar Mercancias (obligatorio, incluye Autotransporte dentro)
            mercancias = self._procesar_mercancias(carta_porte_data)
            
            # Procesar FiguraTransporte (opcional)
            figura_transporte = None
            figura_data = (carta_porte_data.get('cartaporte31:FiguraTransporte') or
                         carta_porte_data.get('FiguraTransporte') or 
                         carta_porte_data.get('figura_transporte'))
            if figura_data:
                figura_transporte = self._procesar_figura_transporte(carta_porte_data)
            
            # Crear objeto CartaPorte con campos obligatorios y opcionales
            # IMPORTANTE: total_dist_rec DEBE pasarse al constructor cuando hay Autotransporte (regla SAT CP125)
            carta_porte = cartaporte31.CartaPorte(
                transp_internac=transp_internac,
                id_ccp=id_ccp,
                ubicaciones=ubicaciones,
                mercancias=mercancias,
                total_dist_rec=total_dist_rec,  # Pasar al constructor, no asignar después
                figura_transporte=figura_transporte  # También pasar al constructor
            )
            
            return carta_porte
            
        except Exception as e:
            raise ValueError(f"Error al procesar CartaPorte: {str(e)}")
    
    def _procesar_ubicaciones(self, carta_porte_data: Dict[str, Any]) -> List[cartaporte31.Ubicacion]:
        """
        Procesa la lista de ubicaciones de Carta Porte.
        """
        # Buscar con prefijo cartaporte31: primero
        ubicaciones_container = (carta_porte_data.get('cartaporte31:Ubicaciones') or 
                                carta_porte_data.get('Ubicaciones') or
                                carta_porte_data.get('ubicaciones'))
        
        if ubicaciones_container:
            ubicaciones_data = (ubicaciones_container.get('cartaporte31:Ubicacion') or
                              ubicaciones_container.get('Ubicacion') or
                              ubicaciones_container.get('ubicacion'))
        else:
            ubicaciones_data = None
        
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
            
            # Campos obligatorios según la API de satcfdi
            rfc_remitente_destinatario = (ub_data.get('RFCRemitenteDestinatario') or 
                                         ub_data.get('rfc_remitente_destinatario'))
            if not rfc_remitente_destinatario:
                raise ValueError(f"RFCRemitenteDestinatario es obligatorio en Ubicacion {idx}")
            
            fecha_hora_salida_llegada_str = (ub_data.get('FechaHoraSalidaLlegada') or 
                                            ub_data.get('fecha_hora_salida_llegada'))
            if not fecha_hora_salida_llegada_str:
                raise ValueError(f"FechaHoraSalidaLlegada es obligatorio en Ubicacion {idx}")
            
            # Convertir fecha/hora a datetime
            if isinstance(fecha_hora_salida_llegada_str, str):
                try:
                    fecha_hora_salida_llegada = datetime.fromisoformat(fecha_hora_salida_llegada_str)
                except ValueError:
                    fecha_hora_salida_llegada = datetime.strptime(fecha_hora_salida_llegada_str, '%Y-%m-%d %H:%M:%S')
            else:
                fecha_hora_salida_llegada = fecha_hora_salida_llegada_str
            
            # Preparar campos opcionales ANTES de crear Ubicacion
            id_ubicacion = ub_data.get('IDUbicacion') or ub_data.get('id_ubicacion')
            nombre_remitente_destinatario = (ub_data.get('NombreRemitenteDestinatario') or 
                                            ub_data.get('nombre_remitente_destinatario'))
            
            # DistanciaRecorrida - CRÍTICO para CP141 cuando hay Autotransporte
            distancia_recorrida = ub_data.get('DistanciaRecorrida') or ub_data.get('distancia_recorrida')
            if distancia_recorrida:
                distancia_recorrida = Decimal(str(distancia_recorrida))
            
            # Procesar Domicilio
            domicilio = None
            domicilio_data = (ub_data.get('cartaporte31:Domicilio') or
                            ub_data.get('Domicilio') or 
                            ub_data.get('domicilio'))
            if domicilio_data:
                domicilio = self._procesar_domicilio(domicilio_data)
            
            # Crear objeto Ubicacion con TODOS los campos en el constructor
            ubicacion = cartaporte31.Ubicacion(
                tipo_ubicacion=tipo_ubicacion,
                rfc_remitente_destinatario=rfc_remitente_destinatario,
                fecha_hora_salida_llegada=fecha_hora_salida_llegada,
                id_ubicacion=id_ubicacion,
                nombre_remitente_destinatario=nombre_remitente_destinatario,
                distancia_recorrida=distancia_recorrida,  # DEBE estar en constructor para CP141
                domicilio=domicilio
            )
            
            ubicaciones.append(ubicacion)
        
        if len(ubicaciones) < 2:
            raise ValueError("Debe haber al menos 2 ubicaciones en CartaPorte (origen y destino)")
        
        return ubicaciones
    
    def _procesar_domicilio(self, domicilio_data: Dict[str, Any]) -> cartaporte31.Domicilio:
        """
        Procesa los datos del domicilio de una ubicación.
        """
        # Campos obligatorios según la API de satcfdi
        pais = domicilio_data.get('Pais') or domicilio_data.get('pais')
        if not pais:
            raise ValueError("Pais es obligatorio en Domicilio")
        
        estado = domicilio_data.get('Estado') or domicilio_data.get('estado')
        if not estado:
            raise ValueError("Estado es obligatorio en Domicilio")
        
        codigo_postal = domicilio_data.get('CodigoPostal') or domicilio_data.get('codigo_postal')
        if not codigo_postal:
            raise ValueError("CodigoPostal es obligatorio en Domicilio")
        
        # Calle - requerido por la plantilla HTML de satcfdi aunque el SAT lo permita opcional en algunos casos
        calle = domicilio_data.get('Calle') or domicilio_data.get('calle') or 'SIN CALLE'
        
        # Crear objeto Domicilio con campos obligatorios y Calle
        domicilio = cartaporte31.Domicilio(
            pais=pais,
            estado=estado,
            codigo_postal=codigo_postal,
            calle=calle  # Incluir Calle en el constructor para evitar errores en plantilla HTML
        )
        
        # Campos opcionales
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
        
        return domicilio
    
    def _procesar_mercancias(self, carta_porte_data: Dict[str, Any]) -> cartaporte31.Mercancias:
        """
        Procesa la sección de Mercancías de Carta Porte.
        NOTA: Autotransporte va DENTRO de Mercancias según satcfdi
        """
        mercancias_data = (carta_porte_data.get('cartaporte31:Mercancias') or
                          carta_porte_data.get('Mercancias') or 
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
        
        num_total_mercancias = (mercancias_data.get('NumTotalMercancias') or 
                               mercancias_data.get('num_total_mercancias'))
        if not num_total_mercancias:
            raise ValueError("NumTotalMercancias es obligatorio en Mercancias")
        
        # Procesar lista de Mercancia
        mercancia_list = self._procesar_lista_mercancias(mercancias_data)
        
        # Procesar Autotransporte (opcional pero esperado por satcfdi)
        autotransporte_data = (mercancias_data.get('cartaporte31:Autotransporte') or
                              mercancias_data.get('Autotransporte') or 
                              mercancias_data.get('autotransporte'))
        
        autotransporte = None
        if autotransporte_data:
            autotransporte = self._procesar_autotransporte(autotransporte_data)
        
        # Crear objeto Mercancias
        mercancias = cartaporte31.Mercancias(
            peso_bruto_total=Decimal(str(peso_bruto_total)),
            unidad_peso=unidad_peso,
            num_total_mercancias=int(num_total_mercancias),
            mercancia=mercancia_list,
            autotransporte=autotransporte  # Pasar Autotransporte a Mercancias
        )
        
        return mercancias
    
    def _procesar_lista_mercancias(self, mercancias_data: Dict[str, Any]) -> List[cartaporte31.Mercancia]:
        """
        Procesa la lista individual de mercancías.
        """
        mercancia_list_data = (mercancias_data.get('cartaporte31:Mercancia') or
                              mercancias_data.get('Mercancia') or 
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
            
            # Campos opcionales (preparar antes de crear objeto)
            material_peligroso = merc_data.get('MaterialPeligroso') or merc_data.get('material_peligroso')
            unidad = merc_data.get('Unidad') or merc_data.get('unidad')
            valor_mercancia = merc_data.get('ValorMercancia') or merc_data.get('valor_mercancia')
            if valor_mercancia:
                valor_mercancia = Decimal(str(valor_mercancia))
            moneda = merc_data.get('Moneda') or merc_data.get('moneda')
            fraccion_arancelaria = (merc_data.get('FraccionArancelaria') or 
                                   merc_data.get('fraccion_arancelaria'))
            uuid_comercio_ext = merc_data.get('UUIDComercioExt') or merc_data.get('uuid_comercio_ext')
            
            # Crear objeto Mercancia con campos obligatorios y opcionales en constructor
            # IMPORTANTE: material_peligroso DEBE estar en constructor para CP155
            mercancia = cartaporte31.Mercancia(
                bienes_transp=bienh_transp,
                descripcion=descripcion,
                cantidad=Decimal(str(cantidad)),
                clave_unidad=clave_unidad,
                peso_en_kg=Decimal(str(peso_en_kg)),
                material_peligroso=material_peligroso,  # CP155: Obligatorio para ciertos BienesTransp
                unidad=unidad,
                valor_mercancia=valor_mercancia,
                moneda=moneda,
                fraccion_arancelaria=fraccion_arancelaria,
                uuid_comercio_ext=uuid_comercio_ext
            )
            
            mercancia_list.append(mercancia)
        
        return mercancia_list
    
    def _procesar_autotransporte(self, autotransporte_data: Dict[str, Any]) -> Optional[cartaporte31.Autotransporte]:
        """
        Procesa la sección de Autotransporte.
        Ahora recibe los datos del nodo Autotransporte directamente.
        """
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
        
        # Procesar IdentificacionVehicular (OBLIGATORIO EN SATCFDI)
        id_vehicular_data = (autotransporte_data.get('cartaporte31:IdentificacionVehicular') or
                            autotransporte_data.get('IdentificacionVehicular') or 
                            autotransporte_data.get('identificacion_vehicular'))
        if not id_vehicular_data:
            raise ValueError("IdentificacionVehicular es obligatorio en Autotransporte")
        
        id_vehicular = self._procesar_identificacion_vehicular(id_vehicular_data)
        
        # Procesar Seguros (OBLIGATORIO EN SATCFDI)
        seguros_data = (autotransporte_data.get('cartaporte31:Seguros') or
                       autotransporte_data.get('Seguros') or 
                       autotransporte_data.get('seguros'))
        if not seguros_data:
            raise ValueError("Seguros es obligatorio en Autotransporte")
        
        seguros = self._procesar_seguros(seguros_data)
        
        # Procesar Remolques ANTES de crear Autotransporte (opcional pero puede ser obligatorio según CP184)
        remolques = None
        remolques_data = (autotransporte_data.get('cartaporte31:Remolques') or
                         autotransporte_data.get('Remolques') or 
                         autotransporte_data.get('remolques'))
        if remolques_data:
            remolques = self._procesar_remolques(remolques_data)
        
        # Crear objeto Autotransporte con campos obligatorios y opcionales en constructor
        # IMPORTANTE: remolques DEBE pasar al constructor para CP184
        autotransporte = cartaporte31.Autotransporte(
            perm_sct=perm_sct,
            num_permiso_sct=num_permiso_sct,
            identificacion_vehicular=id_vehicular,
            seguros=seguros,
            remolques=remolques  # CP184: Obligatorio para ciertas configuraciones vehiculares
        )
        
        return autotransporte
    
    def _procesar_transporte_aereo(self, transporte_aereo_data: Dict[str, Any]) -> Optional[Any]:
        """Procesa datos de transporte aéreo"""
        # Implementar según necesidad
        raise NotImplementedError("Transporte Aereo no implementado aún")
    
    def _procesar_transporte_maritimo(self, transporte_maritimo_data: Dict[str, Any]) -> Optional[Any]:
        """Procesa datos de transporte marítimo"""
        # Implementar según necesidad
        raise NotImplementedError("Transporte Maritimo no implementado aún")
    
    def _procesar_transporte_ferroviario(self, transporte_ferroviario_data: Dict[str, Any]) -> Optional[Any]:
        """Procesa datos de transporte ferroviario"""
        # Implementar según necesidad
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
        
        peso_bruto_vehicular = (id_vehicular_data.get('PesoBrutoVehicular') or 
                               id_vehicular_data.get('peso_bruto_vehicular'))
        if not peso_bruto_vehicular:
            raise ValueError("PesoBrutoVehicular es obligatorio en IdentificacionVehicular")
        
        # Crear objeto IdentificacionVehicular
        id_vehicular = cartaporte31.IdentificacionVehicular(
            config_vehicular=config_vehicular,
            placa_vm=placa_vm,
            anio_modelo_vm=int(anio_modelo_vm),
            peso_bruto_vehicular=Decimal(str(peso_bruto_vehicular))
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
        remolque_list_data = (remolques_data.get('cartaporte31:Remolque') or
                             remolques_data.get('Remolque') or 
                             remolques_data.get('remolque'))
        
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
        figura_data = (carta_porte_data.get('cartaporte31:FiguraTransporte') or
                      carta_porte_data.get('FiguraTransporte') or 
                      carta_porte_data.get('figura_transporte'))
        
        if not figura_data:
            return None
        
        tipos_figura_data = (figura_data.get('cartaporte31:TiposFigura') or
                           figura_data.get('TiposFigura') or 
                           figura_data.get('tipos_figura'))
        
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
            
            nombre_figura = tipo_data.get('NombreFigura') or tipo_data.get('nombre_figura')
            if not nombre_figura:
                raise ValueError(f"NombreFigura es obligatorio en TiposFigura {idx}")
            
            # Campos opcionales (preparar antes de crear objeto)
            rfc_figura = tipo_data.get('RFCFigura') or tipo_data.get('rfc_figura')
            num_licencia = tipo_data.get('NumLicencia') or tipo_data.get('num_licencia')
            
            # Crear objeto TiposFigura con todos los campos en constructor
            # IMPORTANTE: Todos los campos deben pasarse al constructor para CP193
            tipo_figura_obj = cartaporte31.TiposFigura(
                tipo_figura=tipo_figura,
                nombre_figura=nombre_figura,
                rfc_figura=rfc_figura,
                num_licencia=num_licencia
            )
            
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