"""
Router de Status - Endpoints para verificación de estatus de CFDI

Este módulo contiene los endpoints relacionados con la verificación de estatus de CFDI,
delegando toda la lógica de negocio a ServiceStatusComprobante.
Nota: Asegurar que xml venga en formato utf-8.
"""

from fastapi import APIRouter, Body
import sys
import os   

# Añadir ruta del backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from Business.ServiceStatusComprobante import ServiceStatusComprobante

# Crear router
router = APIRouter(
    prefix="",
    tags=["Status"]
)


@router.post("/status/",
    summary="Verificar estatus de CFDI",
    description="Verifica el estatus actual de un comprobante CFDI timbrado enviando el XML completo."
)
async def status_endpoint(
    data: dict = Body(
        ...,
        description="Objeto JSON con 'xml_timbrado' (string XML del CFDI timbrado).",
        example={
            "xml_timbrado": "<?xml version='1.0' encoding='UTF-8'?><cfdi:Comprobante ...>...</cfdi:Comprobante>"
        }
    )
):
    
    return ServiceStatusComprobante.verificar_estatus(data)