from fastapi import FastAPI, Request
from CapaDatos.ConvertirJson import ConvertirJson, JsonInput
from CapaDatos.InterpreteJson import InterpreteJson

app = FastAPI()
"""
@app.post("/convertir_json/")
def convertir_json(item: JsonInput):
    converter = ConvertirJson(item.data)
    xml = converter.GenerarXml()
    return {"xml": xml}
"""

@app.post("/InterpreteJson/")
async def procesar_json(request: Request):
    raw_body: str = await request.body()
    raw_body = raw_body.decode("utf-8")

    try:
        interprete = InterpreteJson(raw_body)
    except ValueError as e:
        return {"error": str(e)}

    # Acceso directo a variables
    conceptos_formato = [
        f"Desc: {c.get('descripcion')} - Cant: {c.get('cantidad')} - Precio: {c.get('precioUnitario')}"
        for c in interprete.conceptos
    ]

    return {
        "mensaje": "JSON procesado correctamente",
        "enviarCorreo": interprete.enviar_correo,
        "generarPDF": interprete.generar_pdf,
        "complemento": interprete.complemento,
        "cer": interprete.cer,
        "key": interprete.key,
        "pwdCER": interprete.pwd_cer,
        "usuarioPAC": interprete.usuario_pac,
        "conceptos": conceptos_formato,
    }
