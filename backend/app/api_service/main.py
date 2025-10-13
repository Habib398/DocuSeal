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
from Business.PreferenciasCliente import PreferenciasCliente

# OpenAPI tag metadata shown in Swagger UI
openapi_tags = [
    {
        "name": "Timbrado",
        "description": "Endpoints para timbrado de CFDI (interacción con PAC)"
    },
    {
        "name": "Sellado",
        "description": "Endpoints para sellado de CFDI (generación de sello y cadena original)"
    },
    {
        "name": "Utilities",
        "description": "Health checks y endpoints utilitarios"
    }
]

app = FastAPI(
    title="DocuSeal Service API",
    version="1.0.0",
    description="API pública para servicios de sellado y timbrado de CFDI",
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

# Endpoints públicos de proceso de timbrado y sellado
@app.post("/timbrar/", tags=["Timbrado"], summary="Timbrar CFDI", 
          description="Timbrado de un XML de CFDI previamente sellado. Requiere credenciales del PAC.")

async def timbrar_endpoint(
    xml: str = Body(..., embed=True, description="XML del comprobante con sello (string)", example="<Comprobante>...xml...</Comprobante>"),
    usuario_pac: str = Body(..., embed=True, description="Usuario PAC" , example="miUsuarioPAC"),
    contrasena_pac: str = Body(..., embed=True, description="Contraseña PAC", example="miContrasenaPAC"),
    pruebas: bool = Body(True, embed=True, description="Indica si se usan servicios de prueba del PAC", example=True)
):
    """Timbrar un CFDI usando las credenciales del PAC.

    Retorna la respuesta original del servicio PAC o un objeto con error.
    """
    return TimbradoService.timbrar_cfdi(xml, usuario_pac, contrasena_pac, pruebas)

@app.post("/sellar/", tags=["Sellado"], summary="Sellar CFDI", 
    description="Sellado de un CFDI. Se espera un objeto JSON con la estructura del comprobante y datos necesarios para generar el sello.")

async def sellar_endpoint(data: dict = Body(..., 
    description="Objeto JSON completo con los datos del comprobante a sellar", example={
    "Comprobante": {"Version": "4.0", "Serie": "A", "Folio": "123"},
    "Receptor": {"Rfc": "XAXX010101000", "Nombre": "Cliente Ejemplo"},
    "PAC": {"usuario": "miUsuarioPAC", "contrasena": "miContrasenaPAC"}
})):
    """Sellar un CFDI: devuelve el XML con sello y la cadena original en caso de éxito."""
    return SellarXML.sellar_cfdi(data)

@app.post("/timbrarSellar/", tags=["Timbrado", "Sellado"], summary="Sellar y timbrar CFDI", 
    description="Realiza el sellado y, si las credenciales PAC se proveen, el timbrado. Opcionalmente genera un PDF.")

async def timbrar_sellar_endpoint(data: dict = Body(..., 
    description="Objeto JSON con los datos del comprobante (misma estructura que /sellar) y " \
    "campo PAC para timbrado", example={
    "Comprobante": {"Version": "4.0", "Serie": "A", "Folio": "123"},
    "Receptor": {"Rfc": "XAXX010101000", "Nombre": "Cliente Ejemplo"},
    "PAC": {"usuario": "miUsuarioPAC", "contrasena": "miContrasenaPAC"},
    "generarPDF": True
})):
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
    
    # Leer preferencias del usuario desde el JSON
    preferencias = PreferenciasCliente.from_json(data)
    
    # Generar HTML del PDF si el usuario lo solicitó
    if preferencias.enviarPDF:
        uuid = resultado_timbrado.get("uuid", "temp")
        pdf_info = PDF.generar_desde_datos(data, xml_sellado, cadena_original, uuid)
        respuesta.update(pdf_info)
    else:
        respuesta["html_generado"] = False
        respuesta["motivo"] = "Usuario no solicitó generación de PDF"
    
    return respuesta

# Endpoint para recibir archivos (CER y KEY)
@app.post("/upload_certificados/", tags=["Utilities"], summary="Subir certificados", 
    description="Sube archivos de certificado (CER) y llave privada (KEY) para uso en sellado.")
async def upload_certificados(cer: bytes = Body(..., description="Contenido del archivo .cer", example=b"-----BEGIN CERTIFICATE-----..."),
                             key: bytes = Body(..., description="Contenido del archivo .key", example=b"-----BEGIN PRIVATE KEY-----..."),
                             password: str = Body(..., description="Contraseña de la llave privada", example="miPasswordKey")):
    # Aquí se procesarían los archivos y la contraseña
    return {"mensaje": "Certificados subidos exitosamente"}