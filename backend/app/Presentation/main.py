from fastapi import FastAPI
from fastapi import Body
from Business.SellarXML import SellarXML
from Business.Timbrado import TimbradoService

app = FastAPI()
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
    
    # Obtiene credenciales PAC
    usuario_pac = data.get("PAC", {}).get("usuario")
    contrasena_pac = data.get("PAC", {}).get("contrasena")
    pruebas = data.get("pruebas", True)
    
    if not usuario_pac or not contrasena_pac:
        return {"error": "Faltan credenciales PAC (objeto PAC incompleto o vacío)"}
    
    # Timbrado
    return TimbradoService.timbrar_cfdi(xml_sellado, usuario_pac, contrasena_pac, pruebas)