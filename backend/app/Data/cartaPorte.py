from decimal import Decimal
from datetime import datetime

# importa las clases del módulo cartaporte30
from satcfdi.create.cfd.cartaporte30 import (
    CartaPorte,
    Ubicacion,
    Domicilio,
    Mercancia,
    Mercancias,
    Autotransporte,
    IdentificacionVehicular,
    Seguros,
    Remolque,
)


class CartaPorteBuilder:
    def __init__(self, datos_carta_porte: dict):
        self.datos_cp = datos_carta_porte

    def construir(self) -> CartaPorte:
        # Construye y retorna el objeto CartaPorte completo.
        # Extraer datos principales
        version = self.datos_cp.get("Version", "3.0")
        id_ccp = self.datos_cp.get("IdCCP", "")
        transp_internac = self.datos_cp.get("TranspInternac", "No")
        total_dist_rec = self._to_decimal(self.datos_cp.get("TotalDistRec"))

        # Construir ubicaciones
        ubicaciones = self._construir_ubicaciones()

        # Construir mercancías
        mercancias = self._construir_mercancias()

        # Construir CartaPorte
        carta_porte = CartaPorte(
            version=version,
            id_ccp=id_ccp,
            transp_internac=transp_internac,
            total_dist_rec=total_dist_rec,
            ubicaciones=ubicaciones,
            mercancias=mercancias
        )

        return carta_porte

    def _construir_ubicaciones(self) -> list:
        # Construye la lista de ubicaciones (origen/destino) desde el JSON.
        ubicaciones = []
        datos_ubicaciones = self.datos_cp.get("cartaporte30:Ubicaciones", {})
        lista_ubicaciones = datos_ubicaciones.get("cartaporte30:Ubicacion", [])
        if isinstance(lista_ubicaciones, dict):
            lista_ubicaciones = [lista_ubicaciones]
        for ubi_data in lista_ubicaciones:
            # Construir domicilio si existe
            domicilio = None
            if "cartaporte30:Domicilio" in ubi_data:
                domicilio = self._construir_domicilio(ubi_data["cartaporte30:Domicilio"])

            # Parsear fecha/hora
            fecha_hora_str = ubi_data.get("FechaHoraSalidaLlegada", "")
            fecha_hora = self._parse_datetime(fecha_hora_str)

            # Crear ubicación
            ubicacion = Ubicacion(
                tipo_ubicacion=ubi_data.get("TipoUbicacion", ""),
                id_ubicacion=ubi_data.get("IDUbicacion", ""),
                rfc_remitente_destinatario=ubi_data.get("RFCRemitenteDestinatario", ""),
                nombre_remitente_destinatario=ubi_data.get("NombreRemitenteDestinatario", ""),
                num_reg_id_trib=ubi_data.get("NumRegIdTrib") or None,
                residencia_fiscal=ubi_data.get("ResidenciaFiscal") or None,
                num_estacion=ubi_data.get("NumEstacion") or None,
                nombre_estacion=ubi_data.get("NombreEstacion") or None,
                navegacion_trafico=ubi_data.get("NavegacionTrafico") or None,
                fecha_hora_salida_llegada=fecha_hora,
                tipo_estacion=ubi_data.get("TipoEstacion") or None,
                distancia_recorrida=self._to_decimal(ubi_data.get("DistanciaRecorrida")),
                domicilio=domicilio
            )
            ubicaciones.append(ubicacion)

        return ubicaciones

    def _construir_domicilio(self, dom_data: dict) -> Domicilio:
        # Construye un objeto Domicilio desde el JSON.
        return Domicilio(
            calle=dom_data.get("Calle") or None,
            numero_exterior=dom_data.get("NumeroExterior") or None,
            numero_interior=dom_data.get("NumeroInterior") or None,
            colonia=dom_data.get("Colonia") or None,
            localidad=dom_data.get("Localidad") or None,
            referencia=dom_data.get("Referencia") or None,
            municipio=dom_data.get("Municipio") or None,
            estado=dom_data.get("Estado", ""),
            pais=dom_data.get("Pais", ""),
            codigo_postal=dom_data.get("CodigoPostal", "")
        )

    def _construir_mercancias(self) -> Mercancias:
        # Construye el objeto Mercancias con todas las mercancías y autotransporte.
        datos_mercancias = self.datos_cp.get("cartaporte30:Mercancias", {})

        # Construir lista de mercancías
        lista_mercancias = []
        merc_data = datos_mercancias.get("cartaporte30:Mercancia", [])
        
        # Si es un solo elemento, convertir a lista
        if isinstance(merc_data, dict):
            merc_data = [merc_data]

        for m in merc_data:
            mercancia = self._construir_mercancia(m)
            lista_mercancias.append(mercancia)

        # Construir autotransporte si existe
        autotransporte = None
        if "cartaporte30:Autotransporte" in datos_mercancias:
            autotransporte = self._construir_autotransporte(
                datos_mercancias["cartaporte30:Autotransporte"]
            )

        # Crear objeto Mercancias
        mercancias = Mercancias(
            peso_bruto_total=self._to_decimal(datos_mercancias.get("PesoBrutoTotal", "0")),
            unidad_peso=datos_mercancias.get("UnidadPeso", "KGM"),
            peso_neto_total=self._to_decimal(datos_mercancias.get("PesoNetoTotal")),
            num_total_mercancias=int(datos_mercancias.get("NumTotalMercancias", 1)),
            cargo_por_tasacion=self._to_decimal(datos_mercancias.get("CargoPorTasacion")),
            mercancia=lista_mercancias,
            autotransporte=autotransporte
        )

        return mercancias

    def _construir_mercancia(self, merc_data: dict) -> Mercancia:
        # Construye un objeto Mercancia desde el JSON.
        return Mercancia(
            bienes_transp=merc_data.get("BienesTransp", ""),
            clave_stcc=merc_data.get("ClaveSTCC") or None,
            descripcion=merc_data.get("Descripcion", ""),
            cantidad=self._to_decimal(merc_data.get("Cantidad", "1")),
            clave_unidad=merc_data.get("ClaveUnidad", ""),
            unidad=merc_data.get("Unidad") or None,
            dimensiones=merc_data.get("Dimensiones") or None,
            material_peligroso=merc_data.get("MaterialPeligroso") or None,
            cve_material_peligroso=merc_data.get("CveMaterialPeligroso") or None,
            embalaje=merc_data.get("Embalaje") or None,
            descrip_embalaje=merc_data.get("DescripEmbalaje") or None,
            sector_cofepris=merc_data.get("SectorCOFEPRIS") or None,
            nombre_ingrediente_activo=merc_data.get("NombreIngredienteActivo") or None,
            nom_quimico_elemento_conc=merc_data.get("NomQuimicoElementoConc") or None,
            denominacion_generica=merc_data.get("DenominacionGenerica") or None,
            denominacion_distintiva=merc_data.get("DenominacionDistintiva") or None,
            fabricante=merc_data.get("Fabricante") or None,
            fecha_fabricacion=self._parse_date(merc_data.get("FechaFabricacion")),
            fecha_caducidad=self._parse_date(merc_data.get("FechaCaducidad")),
            lote_medicamento=merc_data.get("LoteMedicamento") or None,
            forma_farmaceutica=merc_data.get("FormaFarmaceutica") or None,
            condiciones_esp_transp=merc_data.get("CondicionesEspTransp") or None,
            registro_sanitario_folio_autorizacion=merc_data.get("RegistroSanitarioFolioAutorizacion") or None,
            peso_en_kg=self._to_decimal(merc_data.get("PesoEnKg", "0")),
            valor_mercancia=self._to_decimal(merc_data.get("ValorMercancia")),
            moneda=merc_data.get("Moneda") or None,
            fraccion_arancelaria=merc_data.get("FraccionArancelaria") or None,
            uuid_comercio_ext=merc_data.get("UUIDComercioExt") or None
        )

    def _construir_autotransporte(self, auto_data: dict) -> Autotransporte:
        # Construye el objeto Autotransporte desde el JSON.
        # Construir identificación vehicular
        ident_vehicular = None
        if "cartaporte30:IdentificacionVehicular" in auto_data:
            ident_data = auto_data["cartaporte30:IdentificacionVehicular"]
            ident_vehicular = IdentificacionVehicular(
                config_vehicular=ident_data.get("ConfigVehicular", ""),
                placa_vm=ident_data.get("PlacaVM", ""),
                anio_modelo_vm=int(ident_data.get("AnioModeloVM", 0))
            )

        # Construir seguros
        seguros = None
        if "cartaporte30:Seguros" in auto_data:
            seg_data = auto_data["cartaporte30:Seguros"]
            seguros = Seguros(
                asegura_resp_civil=seg_data.get("AseguraRespCivil", ""),
                poliza_resp_civil=seg_data.get("PolizaRespCivil", ""),
                asegura_med_ambiente=seg_data.get("AseguraMedAmbiente") or None,
                poliza_med_ambiente=seg_data.get("PolizaMedAmbiente") or None,
                asegura_carga=seg_data.get("AseguraCarga") or None,
                poliza_carga=seg_data.get("PolizaCarga") or None,
                prima_seguro=self._to_decimal(seg_data.get("PrimaSeguro"))
            )

        # Construir remolques
        remolques = []
        if "cartaporte30:Remolques" in auto_data:
            rem_data = auto_data["cartaporte30:Remolques"].get("cartaporte30:Remolque", [])
            if isinstance(rem_data, dict):
                rem_data = [rem_data]
            
            for r in rem_data:
                remolque = Remolque(
                    sub_tipo_rem=r.get("SubTipoRem", ""),
                    placa=r.get("Placa", "")
                )
                remolques.append(remolque)

        # Crear autotransporte
        autotransporte = Autotransporte(
            perm_sct=auto_data.get("PermSCT", ""),
            num_permiso_sct=auto_data.get("NumPermisoSCT", ""),
            identificacion_vehicular=ident_vehicular,
            seguros=seguros,
            remolques=remolques if remolques else None
        )

        return autotransporte

    def _to_decimal(self, valor) -> Decimal:
        # Convierte un valor a Decimal. Si es None o vacío, retorna None.
        if valor is None or valor == "":
            return None
        try:
            return Decimal(str(valor))
        except:
            return None

    def _parse_datetime(self, fecha_str: str) -> datetime:
        # Parsea una cadena de fecha/hora en formato ISO.
        if not fecha_str:
            return datetime.now()
        try:
            return datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        except:
            return datetime.now()

    def _parse_date(self, fecha_str: str):
        # Parsea una cadena de fecha en formato ISO (YYYY-MM-DD).
        if not fecha_str:
            return None
        try:
            return datetime.fromisoformat(fecha_str).date()
        except:
            return None