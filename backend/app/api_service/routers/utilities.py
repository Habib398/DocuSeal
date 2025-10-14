"""
Router de Utilities - Endpoints utilitarios

Este módulo contiene endpoints de utilidad.
"""

from fastapi import APIRouter, Body

# Crear router
router = APIRouter(
    prefix="",
    tags=["Utilities"]
)

@router.post(
    "/upload_certificados/",
    summary="Subir certificados",
    description="Sube archivos de certificado (CER) y llave privada (KEY) para uso en sellado."
)
async def upload_certificados(
    cer: bytes = Body(..., description="Contenido del archivo .cer", example=b"-----BEGIN CERTIFICATE-----..."),
    key: bytes = Body(..., description="Contenido del archivo .key", example=b"-----BEGIN PRIVATE KEY-----..."),
    password: str = Body(..., description="Contraseña de la llave privada", example="miPasswordKey")
):
    return {
        "mensaje": "Certificados subidos exitosamente",
        "status": "pendiente_implementacion"
    }
