"""
Módulo de Cancelación Multi-PAC.

Este paquete contiene la infraestructura para soportar
cancelaciones de CFDIs con múltiples proveedores PAC.

NOTA: Renombrado a CancelacionPACs para evitar conflicto
con el archivo Cancelacion.py (wrapper de compatibilidad).
"""

from .CancelacionPAC import CancelacionPAC, CancelacionPACException
from .CancelacionComercioDigital import CancelacionComercioDigital
from .CancelacionGenericaPAC import CancelacionGenericaPAC

__all__ = [
    'CancelacionPAC', 
    'CancelacionPACException',
    'CancelacionComercioDigital',
    'CancelacionGenericaPAC'
]
