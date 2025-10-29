"""
Router de Sellado - Endpoints para sellado de CFDI

Este módulo contiene los endpoints relacionados con el sellado de CFDI,
delegando toda la lógica de negocio a ServicioSellado y ServicioTimbrarSellar.
"""
import sys
import os

from fastapi import APIRouter, Body

# Añadir ruta del backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from Business.ServicioSellado import ServicioSellado
from Business.ServicioTimbrarSellar import ServicioTimbrarSellar
from Business.cfdi.ComprobanteFactory import ComprobanteFactory

# Crear router sin tags globales para poder asignar tags específicos a cada endpoint
router = APIRouter(
    prefix=""
)

@router.post(
    "/sellar/",
    summary="Sellar CFDI",
    description="Sellado de un CFDI. Acepta 'xml' (string XML) o 'datosXML' (estructura JSON con cfdi:Comprobante). Requiere 'claveUsuario'.",
    tags=["Sellado"]
)
async def sellar_endpoint(
    data: dict = Body(
        ...,
        description="Objeto JSON con 'xml' (string XML) o 'datosXML' (estructura JSON del comprobante) y 'claveUsuario'.",
        example={
            "datosXML(JSON) o xml(String xml)": "",
            "claveUsuario": "550e8400-e29b-41d4-a716-446655440000",
            "enviarCorreo": False,
            "generarPDF": False
        }
    )
):
    # Procesar comprobante si se envía datosXML
    if "datosXML" in data:
        resultado = ComprobanteFactory.procesar_comprobante(data["datosXML"])
        if not resultado["valido"]:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "mensaje": "Errores de validación en el comprobante",
                    "errores": resultado["errores"],
                    "warnings": resultado["warnings"]
                }
            )
        # Reemplazar datosXML con el XML generado
        data["xml"] = resultado["xml"]
        del data["datosXML"]
    
    return ServicioSellado.sellar(data)


@router.post(
    "/timbrarSellar/",
    summary="Sellar y timbrar CFDI",
    description="Realiza el sellado y timbrado completo. Acepta 'xml' (string XML) o 'datosXML' (estructura JSON con cfdi:Comprobante). "
                "Opcionalmente genera PDF y envía correo. Requiere 'claveUsuario' para obtener credenciales PAC.",
    tags=["Timbrado y Sellado"]
)
async def timbrar_sellar_endpoint(
    data: dict = Body(
        ...,
        description="JSON con 'xml' (string XML) o 'datosXML' (estructura JSON del comprobante) y 'claveUsuario'. "
                    "Las credenciales PAC se obtienen automáticamente. El modo de pruebas se toma del certificado.",
        example={
            "datosXML(JSON) o xml(String xml)": {},
            "claveUsuario": "550e8400-e29b-41d4-a716-446655440000",
            "enviarCorreo": False,
            "generarPDF": False
        }
    )
):
    # Procesar comprobante si se envía datosXML
    if "datosXML" in data:
        resultado = ComprobanteFactory.procesar_comprobante(data["datosXML"])
        if not resultado["valido"]:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "mensaje": "Errores de validación en el comprobante",
                    "errores": resultado["errores"],
                    "warnings": resultado["warnings"]
                }
            )
        # Reemplazar datosXML con el XML generado
        data["xml"] = resultado["xml"]
        del data["datosXML"]
    
    return ServicioTimbrarSellar.procesar(data)
