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
from routers import timbrado, sellado, utilities

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
        "name": "Utilities",
        "description": "Health checks y endpoints utilitarios"
    }
]

# Inicializando FastAPI
app = FastAPI(
    title="DocuSeal Service API",
    version="1.6.0",
    description="API pública para servicios de sellado y timbrado de CFDI. "
                "Soporta 'xml' (string XML) y 'datosXML' (estructura JSON).",
    openapi_tags=openapi_tags,
)

# Configurar CORS permisivo para servicio público
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
app.include_router(utilities.router)
