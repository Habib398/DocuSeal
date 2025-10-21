"""
Router de Timbrado - Endpoints para timbrado de CFDI

Este módulo contiene los endpoints relacionados con el timbrado de CFDI,
delegando toda la lógica de negocio a ServicioTimbrado.
"""

from fastapi import APIRouter, Body
import sys
import os   

# Añadir ruta del backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from Business.ServicioTimbrado import ServicioTimbrado

# Crear router
router = APIRouter(
    prefix="",
    tags=["Timbrado"]
)


@router.post("/timbrar/",
    summary="Timbrar CFDI",
    description="Timbrado de un XML de CFDI previamente sellado. Las credenciales del PAC se obtienen automáticamente de la BD usando el NoCertificado del XML."
)
async def timbrar_endpoint(
    data: dict = Body(
        ...,
        description="Objeto JSON con 'xml' (string XML sellado completo). Las credenciales PAC se recuperan automáticamente según el NoCertificado.",
        example={
            "xml": "",
            "pruebas": True
        }
    )
):
    
    return ServicioTimbrado.timbrar(data)
