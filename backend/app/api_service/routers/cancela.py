"""
Router de Cancelación - Endpoints para cancelación de CFDI

Este módulo contiene los endpoints relacionados con la cancelación de CFDI,
delegando toda la lógica de negocio a ServicioCancelacion.
"""

from fastapi import APIRouter, Body
import sys
import os   

# Añadir ruta del backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from Business.Services.ServicioCancelacion import ServicioCancelacion

# Crear router
router = APIRouter(
    prefix="",
    tags=["Cancelación"]
)


@router.post(
    "/cancelar/",
    summary="Cancelar CFDI",
    description="Cancela uno o más comprobantes CFDI mediante el PAC. Se requiere claveUsuario para obtener "
                "certificados y credenciales PAC desde la base de datos. Utiliza satcfdi para el proceso de "
                "firma digital y comunicación con el PAC Comercio Digital."
)
async def cancelar_endpoint(
    data: dict = Body(
        ...,
        description="JSON con claveUsuario y lista de folios a cancelar. Cada folio debe incluir: uuid, "
                    "rfcReceptor, total, tipoComprobante, motivo y opcionalmente folioSustitucion (si motivo=01). "
                    "Los certificados y credenciales PAC se obtienen automáticamente de la BD.",
        example={
            "claveUsuario": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX",
            "folios": [
                {
                    "uuid": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX",
                    "rfcReceptor": "XAXX010101000",
                    "total": "1000.00",
                    "tipoComprobante": "X",
                    "motivo": "02",
                    "folioSustitucion": None
                }
            ],
            "emailEmisor": "emisor@example.com",
            "emailReceptor": "receptor@example.com",
            "guardarAcuse": True
        }
    )
):
    return ServicioCancelacion.cancelar(data)
