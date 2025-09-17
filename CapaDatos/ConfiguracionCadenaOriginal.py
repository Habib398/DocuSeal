
from __future__ import annotations
from typing import Union
import os
from lxml import etree
from CapaDatos.ConvertirJson import ConvertirJson

class CadenaOriginalGenerator:
	# Clase generada por Copilot
	# Nombre del archivo XSLT
	XSLT_FILENAME = "cadenaoriginal_4_0.xslt"
	@classmethod
	def _resolver_ruta_xslt(cls) -> str:
		"""Resuelve la ruta absoluta del XSLT, validando su existencia."""
		base_dir = os.path.dirname(__file__)
		xslt_path = os.path.abspath(os.path.join(base_dir, cls.XSLT_FILENAME))
		if not os.path.exists(xslt_path):
			# Intentar rutas alternativas mínimas (por si estructura cambia)
			alternativas = [
				os.path.join(base_dir, '..', 'CapaDatos', cls.XSLT_FILENAME),
				os.path.join(os.getcwd(), cls.XSLT_FILENAME),
			]
			for alt in alternativas:
				if os.path.exists(alt):
					return os.path.abspath(alt)
			return xslt_path
		return xslt_path

	@classmethod
	def generar(cls, xml_o_convertidor: Union[str, 'ConvertirJson']) -> str:
		# Obtener XML en texto
		if not isinstance(xml_o_convertidor, str):
			xml_string = xml_o_convertidor.GenerarXmlCFDI()
		else:
			xml_string = xml_o_convertidor

		xslt_path = cls._resolver_ruta_xslt()
		# Parsers seguros
		xslt_parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
		xml_parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, no_network=True, load_dtd=False)

		with open(xslt_path, 'rb') as f:
			xslt_doc = etree.parse(f, parser=xslt_parser)
		transform = etree.XSLT(xslt_doc)

		xml_doc = etree.fromstring(xml_string.encode('utf-8'), parser=xml_parser)

		result_tree = transform(xml_doc)

		cadena_original = str(result_tree)
		cadena_original = cadena_original.replace("\r", "").replace("\n", "").strip()
		# No se valida si la cadena está vacía
		return cadena_original