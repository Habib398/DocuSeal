"""
Router de Sellado - Endpoints para sellado de CFDI

Este módulo contiene los endpoints relacionados con el sellado de CFDI,
delegando toda la lógica de negocio a ServicioSellado y ServicioTimbrarSellar.
"""

from fastapi import APIRouter, Body
import sys
import os

# Añadir ruta del backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from Business.ServicioSellado import ServicioSellado
from Business.ServicioTimbrarSellar import ServicioTimbrarSellar

# Crear router sin tags globales para poder asignar tags específicos a cada endpoint
router = APIRouter(
    prefix=""
)


@router.post(
    "/sellar/",
    summary="Sellar CFDI",
    description="Sellado de un CFDI. Acepta 'xml' (string XML) o 'datosXML' (estructura JSON). "
                "Requiere credenciales del certificado (pwdCER) para desencriptar la llave privada.",
    tags=["Sellado"]
)
async def sellar_endpoint(
    data: dict = Body(
        ...,
        description="Objeto JSON con 'xml' (XML string) o 'datosXML' (estructura JSON del comprobante) y credenciales del certificado.",
        example={
            "datosXML": {
                "cfdi:Comprobante": {
                    "Version": "4.0",
                    "Serie": "A",
                    "Folio": "123",
                    "NoCertificado": "30001000000300023708"
                }
            },
            "certificado": {"pwdCER": "tu_contraseña"},
            "enviarCorreo": False,
            "generarPDF": False
        }
    )
):
    return ServicioSellado.sellar(data)


@router.post(
    "/timbrarSellar/",
    summary="Sellar y timbrar CFDI",
    description="Realiza el sellado y timbrado. Acepta 'xml' (string XML) o 'datosXML' (estructura JSON). "
                "Opcionalmente genera PDF y envía correo.",
    tags=["Timbrado y Sellado"]
)
async def timbrar_sellar_endpoint(
    data: dict = Body(
        ...,
        description="JSON con 'xml' (string XML) o 'datosXML' (estructura JSON del comprobante). "
                    "Incluir PAC para timbrado, flags para PDF/correo.",
        example={
            "xml": "<Comprobante ...>...</Comprobante>",
            "PAC": {"usuario": "miUsuarioPAC", "contrasena": "miContrasenaPAC"},
            "generarPDF": True,
            "enviarCorreo": False
        }
    )
):
    return ServicioTimbrarSellar.procesar(data)
