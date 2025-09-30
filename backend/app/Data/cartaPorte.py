from lxml import etree
from typing import Optional

try:
    from satcfdi.create.cfd.cartaporte30 import CartaPorte as SatCartaPorte
except Exception:
    SatCartaPorte = None
from datetime import datetime


class CartaPorteBuilder:
    """Adaptador para construir el elemento XML de CartaPorte usando la librería satcfdi.

    Usa `SatCartaPorte.to_xml()` para obtener un `lxml.etree.Element` listo para anexar
    al `<cfdi:Complemento>`.
    """

    @staticmethod
    def build_element(carta_data: dict) -> Optional[etree._Element]:
        if not carta_data:
            return None

        if SatCartaPorte is None:
            raise RuntimeError('satcfdi no está disponible en el entorno')

        # Intentar obtener nodos con o sin prefijo 'cartaporte30:'
        ubicaciones = carta_data.get('cartaporte30:Ubicaciones') or carta_data.get('Ubicaciones')
        mercancias = carta_data.get('cartaporte30:Mercancias') or carta_data.get('Mercancias')
        figura = carta_data.get('FiguraTransporte') or carta_data.get('cartaporte30:FiguraTransporte')

        # Normalizar Ubicaciones: aceptar forma { 'cartaporte30:Ubicacion': [...] } o lista directa
        if isinstance(ubicaciones, dict):
            u = ubicaciones.get('cartaporte30:Ubicacion') or ubicaciones.get('Ubicacion')
            if u is None:
                ubicaciones = []
            else:
                ubicaciones = u if isinstance(u, list) else [u]
        elif ubicaciones is None:
            ubicaciones = []

        # Normalizar Mercancias: puede venir como dict con 'cartaporte30:Mercancia' o como dict simple
        if isinstance(mercancias, dict):
            m = mercancias.get('cartaporte30:Mercancia') or mercancias.get('Mercancia')
            # si hay múltiples, mantener lista
            if m is None:
                # mantener el dict completo (satcfdi espera un dict con PesoBrutoTotal etc.)
                # y la clave Mercancia como dict único dentro
                mercancias = mercancias
            else:
                mercancias = {'Mercancia': (m if isinstance(m, list) else [m]), **{k: v for k, v in mercancias.items() if k not in ('cartaporte30:Mercancia','Mercancia')}}
        elif mercancias is None:
            mercancias = {}

        # Helper para parsear ISO datetimes si vienen como strings
        def _parse_iso(s):
            if not isinstance(s, str):
                return s
            try:
                # datetime.fromisoformat maneja 'YYYY-MM-DD' y 'YYYY-MM-DDTHH:MM:SS' y offsets
                return datetime.fromisoformat(s)
            except Exception:
                return s

        # Normalizar/parsear fechas en Ubicaciones
        if isinstance(ubicaciones, list):
            for u in ubicaciones:
                if not isinstance(u, dict):
                    continue
                if 'FechaHoraSalidaLlegada' in u and isinstance(u['FechaHoraSalidaLlegada'], str):
                    u['FechaHoraSalidaLlegada'] = _parse_iso(u['FechaHoraSalidaLlegada'])

        # Normalizar/parsear fechas en Mercancias
        # mercancias puede ser dict con clave 'Mercancia' como lista
        if isinstance(mercancias, dict) and 'Mercancia' in mercancias:
            mlist = mercancias.get('Mercancia')
            if isinstance(mlist, list):
                for m in mlist:
                    if not isinstance(m, dict):
                        continue
                    if 'FechaFabricacion' in m and isinstance(m['FechaFabricacion'], str):
                        m['FechaFabricacion'] = _parse_iso(m['FechaFabricacion'])
                    if 'FechaCaducidad' in m and isinstance(m['FechaCaducidad'], str):
                        m['FechaCaducidad'] = _parse_iso(m['FechaCaducidad'])
        elif isinstance(mercancias, dict):
            # If mercancias is a single dict (no 'Mercancia' key), try parse directly
            for key in ('FechaFabricacion', 'FechaCaducidad'):
                if key in mercancias and isinstance(mercancias[key], str):
                    mercancias[key] = _parse_iso(mercancias[key])

        # Mapear campos principales al constructor de satcfdi
        sat_obj = SatCartaPorte(
            id_ccp=carta_data.get('IdCCP') or carta_data.get('IdCCP'),
            transp_internac=carta_data.get('TranspInternac', 'No'),
            ubicaciones=ubicaciones,
            mercancias=mercancias,
            regimen_aduanero=carta_data.get('RegimenAduanero'),
            entrada_salida_merc=carta_data.get('EntradaSalidaMerc'),
            pais_origen_destino=carta_data.get('PaisOrigenDestino'),
            via_entrada_salida=carta_data.get('ViaEntradaSalida'),
            total_dist_rec=carta_data.get('TotalDistRec'),
            registro_istmo=carta_data.get('RegistroISTMO'),
            ubicacion_polo_origen=carta_data.get('UbicacionPoloOrigen'),
            ubicacion_polo_destino=carta_data.get('UbicacionPoloDestino'),
            figura_transporte=figura,
        )

        # Obtener el elemento lxml sin incluir schemaLocation (se manejará en el Comprobante)
        elem = sat_obj.to_xml(include_schema_location=False)
        return elem
