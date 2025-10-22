"""
DocuSeal - Aplicación Principal
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
import sys
import os

# Añadir rutas al path para importaciones
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

# Importar las sub-aplicaciones usando rutas relativas
from api_admin import main as admin_module
from api_service import main as service_module

# Crear aplicación principal
app = FastAPI(
    title="DocuSeal API",
    version="2.0.0",
    description="API unificada de DocuSeal para administración y servicios de CFDI.\n\n"
                "- **Admin Frontend**: Interfaz de usuario\n"
                "- **Admin API**: Gestión de usuarios y certificados\n"
                "- **Service API**: Sellado y timbrado de CFDI",
)

# Configurar CORS global
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar las sub-aplicaciones en rutas específicas
# API Admin en /admin/api para que /admin quede libre para el frontend
app.mount("/admin/api", admin_module.app)
app.mount("/service", service_module.app)

# Ruta al frontend compilado de React
frontend_build_path = os.path.abspath(os.path.join(current_dir, "../..", "Frontend", "react-app", "dist"))

# Verificar si existe el build del frontend
if os.path.exists(frontend_build_path):
    # Verificar si existe la carpeta de assets
    assets_path = os.path.join(frontend_build_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/admin/assets", StaticFiles(directory=assets_path), name="admin_assets")
        print(f"Assets montados desde: {assets_path}")
    else:
        print(f"Carpeta de assets no encontrada: {assets_path}")
    
    # Endpoint para servir el SPA en rutas dinámicas de /admin
    # Este DEBE ir después de montar los archivos estáticos
    @app.get("/admin/{full_path:path}")
    async def serve_admin_spa(full_path: str):
        """Servir el SPA de React para todas las rutas de /admin excepto /admin/api"""
        # Si la ruta empieza con 'api', dejar que lo maneje el mount de /admin/api
        if full_path.startswith("api"):
            return Response(status_code=404)
        
        # Si la ruta empieza con 'assets', no debería llegar aquí (ya está montado)
        # pero por si acaso, retornar 404
        if full_path.startswith("assets"):
            return Response(status_code=404)
        
        # Para cualquier otra ruta, servir el index.html (SPA routing)
        index_path = os.path.join(frontend_build_path, "index.html")
        if os.path.exists(index_path):
            response = FileResponse(index_path)
            # Prevenir caché del HTML para evitar servir versiones antiguas
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        return Response(status_code=404)
    
    @app.get("/admin")
    async def serve_admin_root():
        """Servir el index.html del frontend en /admin"""
        index_path = os.path.join(frontend_build_path, "index.html")
        if os.path.exists(index_path):
            response = FileResponse(index_path)
            # Prevenir caché del HTML para evitar servir versiones antiguas
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        return {
            "error": "Frontend build not found",
            "path": index_path
        }
else:
    # Si no existe el build, redirigir al servidor de desarrollo
    print(f" Frontend build no encontrado en: {frontend_build_path}")
    print(" Ejecuta 'npm run build' en Frontend/react-app para compilar el frontend")
    
    @app.get("/admin")
    async def admin_redirect():
        """Redirigir al servidor de desarrollo del frontend"""
        return {
            "message": "Frontend en modo desarrollo",
            "url": "http://localhost:3000",
            "note": "Para producción, ejecuta 'npm run build' en Frontend/react-app",
            "build_path": frontend_build_path
        }

# Endpoint raíz de la aplicación unificada
@app.get("/")
async def root():
    """
    Endpoint raíz - Información sobre las APIs disponibles
    """
    return {
        "message": "DocuSeal API - Aplicación Unificada",
        "version": "2.0.0",
        "apis": {
            "admin_frontend": {
                "path": "/admin",
                "description": "Interfaz de usuario para administración",
                "note": "Sirve el frontend de React o redirige a http://localhost:3000 en desarrollo"
            },
            "admin_api": {
                "path": "/admin/api",
                "description": "API administrativa para gestión de usuarios y certificados",
                "docs": "/admin/api/docs",
                "health": "/admin/api/health"
            },
            "service": {
                "path": "/service",
                "description": "API pública para sellado y timbrado de CFDI",
                "docs": "/service/docs",
                "health": "/service/health"
            }
        },
        "global_docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check global de la aplicación unificada
    """
    return {
        "status": "ok",
        "message": "DocuSeal API is running",
        "services": {
            "admin": "available at /admin",
            "service": "available at /service"
        }
    }
