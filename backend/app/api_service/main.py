from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import sys
import os

# Añadir rutas al path PRIMERO
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_path)

from Business.SellarXML import SellarXML
from Business.Timbrado import TimbradoService
from Business.PDF import PDF

app = FastAPI(
    title="DocuSeal Service API",
    version="1.0.0",
    description="API pública para servicios de sellado y timbrado de CFDI"
)

# Configurar CORS permisivo para servicio público
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "DocuSeal Service API is running"}

# Endpoints públicos de proceso de timbrado y sellado
@app.post("/timbrar/")
async def timbrar_endpoint(
    xml: str = Body(..., embed=True),
    usuario_pac: str = Body(..., embed=True),
    contrasena_pac: str = Body(..., embed=True),
    pruebas: bool = Body(True, embed=True)
):
    return TimbradoService.timbrar_cfdi(xml, usuario_pac, contrasena_pac, pruebas)

@app.post("/sellar/")
async def sellar_endpoint(data: dict = Body(...)):
    return SellarXML.sellar_cfdi(data)

@app.post("/timbrarSellar/")
async def timbrar_sellar_endpoint(data: dict = Body(...)):
    # Sellado
    resultado_sellado = SellarXML.sellar_cfdi(data)
    if "error" in resultado_sellado:
        return resultado_sellado
    
    xml_sellado = resultado_sellado["xml_con_sello"]
    cadena_original = resultado_sellado.get("cadena_original", "")
    
    # Obtiene credenciales PAC
    usuario_pac = data.get("PAC", {}).get("usuario")
    contrasena_pac = data.get("PAC", {}).get("contrasena")
    pruebas = data.get("pruebas", True)
    
    if not usuario_pac or not contrasena_pac:
        return {"error": "Faltan credenciales PAC (objeto PAC incompleto o vacío)"}
    
    # Timbrado
    resultado_timbrado = TimbradoService.timbrar_cfdi(xml_sellado, usuario_pac, contrasena_pac, pruebas)
    
    # Preparar respuesta
    respuesta = resultado_timbrado.copy()
    respuesta["cadena_original"] = cadena_original
    
    # Generar HTML del PDF si el usuario lo solicita
    generar_pdf = data.get("generarPDF", False)
    if generar_pdf:
        uuid = resultado_timbrado.get("uuid", "temp")
        pdf_info = PDF.generar_desde_datos(data, xml_sellado, cadena_original, uuid)
        respuesta.update(pdf_info)
    
    return respuesta