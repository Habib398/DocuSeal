from satcfdi.pacs import Environment, Accept
from satcfdi.pacs.comerciodigital import ComercioDigital
from satcfdi.cfdi import CFDI

import re
import logging

from .ResultadoTimbrado import ResultadoTimbrado

logger = logging.getLogger(__name__)


class TimbradoService:
	"""Servicio para timbrar CFDI utilizando un PAC."""

	@classmethod
	def timbrar_cfdi(cls, xml: str, usuario_pac: str, contrasena_pac: str, pruebas: bool = True) -> dict:
		# Limpiar XML eliminando declaración de encoding UTF-8
		xml_limpio = re.sub(r"<\?xml[^>]*encoding=['\"]?utf-8['\"]?[^>]*\?>", "", xml, flags=re.IGNORECASE)
		xml_limpio = xml_limpio.strip()

		return cls._procesar_timbrado(xml_limpio, usuario_pac, contrasena_pac, pruebas)

	@classmethod
	def _procesar_timbrado(cls, xml: str, usuario_pac: str, contrasena_pac: str, pruebas: bool = True) -> dict:
		env = Environment.TEST if pruebas else Environment.PRODUCTION
		# Se desea implementar varios pac (Implementar a futuro)
		pac = ComercioDigital(user=usuario_pac, password=contrasena_pac, environment=env)
		cfdi = CFDI.from_string(xml)
		try:
			doc = pac.stamp(cfdi, accept=Accept.XML)
			return ResultadoTimbrado.ResultadoExito(doc)
		except Exception as e:
			logger.exception('Error al timbrar CFDI con el PAC')
			return ResultadoTimbrado.ResultadoError(e)

	# Método de instancia para timbrar
	def timbrar(self, xml: str, usuario_pac: str, contrasena_pac: str, pruebas: bool = True) -> dict:
		return self._procesar_timbrado(xml, usuario_pac, contrasena_pac, pruebas)


timbrado_service = TimbradoService()