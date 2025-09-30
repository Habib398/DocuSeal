from satcfdi.pacs import Environment, Accept
from satcfdi.pacs.comerciodigital import ComercioDigital
from satcfdi.cfdi import CFDI


class TimbradoService:

	@classmethod
	def timbrar_cfdi(cls, xml: str, usuario_pac: str, contrasena_pac: str, pruebas: bool = True) -> dict:
		"""
		Método principal para timbrar un CFDI.
		Maneja la limpieza del XML y el proceso completo de timbrado.
		"""
		import re
		
		# Limpiar XML eliminando declaración de encoding UTF-8
		xml_limpio = re.sub(r"<\?xml[^>]*encoding=['\"]?utf-8['\"]?[^>]*\?>", "", xml, flags=re.IGNORECASE)
		xml_limpio = xml_limpio.strip()
		
		return cls._procesar_timbrado(xml_limpio, usuario_pac, contrasena_pac, pruebas)
	
	@classmethod
	def _procesar_timbrado(cls, xml: str, usuario_pac: str, contrasena_pac: str, pruebas: bool = True) -> dict:
		env = Environment.TEST if pruebas else Environment.PRODUCTION
		pac = ComercioDigital(user=usuario_pac, password=contrasena_pac, environment=env)
		cfdi = CFDI.from_string(xml)
		try:
			doc = pac.stamp(cfdi, accept=Accept.XML)
			return {
				"codigo": 0,
				"mensaje": "Timbrado exitoso",
				"uuid": doc.document_id,
				"cuerpo": doc.xml.decode("utf-8") if isinstance(doc.xml, (bytes, bytearray)) else doc.xml,
			}
		except Exception as e:
			msg = str(e)
			uuid = None
			cuerpo = None
			try:
				r = getattr(e, 'response', None)
				if r is not None:
					msg = r.headers.get('errmsg', msg)
					uuid = r.headers.get('uuid')
					cuerpo = r.text
					codigo = r.headers.get('codigo', '-1')
				else:
					codigo = '-1'
			except Exception:
				codigo = '-1'

			return {
				"codigo": codigo,
				"mensaje": msg,
				"uuid": uuid,
				"cuerpo": cuerpo,
			}

	def timbrar(self, xml: str, usuario_pac: str, contrasena_pac: str, pruebas: bool = True) -> dict:
		return self._procesar_timbrado(xml, usuario_pac, contrasena_pac, pruebas)
		
timbrado_service = TimbradoService()