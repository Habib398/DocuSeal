"""
DocuSeal Service API - Main Application

API pública para servicios de sellado y timbrado de CFDI.
Arquitectura modular con routers y services separados.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Añadir rutas al path PRIMERO
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

# Importar routers
from routers import timbrado, sellado, status, cancela

# OpenAPI Swagger UI
openapi_tags = [
    {
        "name": "Timbrado",
        "description": "Endpoint para timbrado de CFDI (interacción con PAC)"
    },
    {
        "name": "Sellado",
        "description": "Endpoint para sellado de CFDI (generación de sello y cadena original)"
    },
    {
        "name": "Timbrado y Sellado",
        "description": "Endpoint para timbrado y sellado de CFDI"
    },
    {
        "name": "Cancelación",
        "description": "Endpoint para cancelación de CFDI mediante PAC"
    },
    {
        "name": "Status",
        "description": "Endpoint para verificación de estatus de CFDI"
    }
]

# Inicializando FastAPI
app = FastAPI(
    title="DocuSeal Service API",
    version="1.6.0",
    description="API pública para servicios de sellado y timbrado de CFDI. "
                "Soporta 'xml' (string XML) y 'datosXML' (estructura JSON).",
    openapi_tags=openapi_tags,
    root_path="/service"  # Configuración para sub-aplicación montada
)

# Configurar CORS permisivo para servicio público
# Nota: Si se monta en la app principal, el CORS se maneja globalmente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Llamada a routers
app.include_router(timbrado.router)
app.include_router(sellado.router)
app.include_router(cancela.router)
app.include_router(status.router)
