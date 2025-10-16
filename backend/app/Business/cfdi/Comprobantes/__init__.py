"""
Módulo de Comprobantes CFDI
Exporta las clases específicas para cada tipo de comprobante
"""

from .Ingreso import ComprobanteIngreso
from .Traslados import ComprobanteTraslado

__all__ = [
    "ComprobanteIngreso",
    "ComprobanteTraslado",
]
