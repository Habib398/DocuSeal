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
    description="Timbrado de un XML de CFDI previamente sellado. Se requiere claveUsuario para identificar el certificado. Opcionalmente genera PDF."
)
async def timbrar_endpoint(
    data: dict = Body(
        ...,
        description="Objeto JSON con 'xml' (string XML sellado completo), 'claveUsuario' para obtener credenciales PAC, y 'generarPDF' (opcional).",
        example={
            "xml": "",
            "claveUsuario": "550e8400-e29b-41d4-a716-446655440000",
            "pruebas": True,
            "generarPDF": False
        }
    )
):
    
    return ServicioTimbrado.timbrar(data)
