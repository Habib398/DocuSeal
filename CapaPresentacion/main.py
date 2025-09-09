from fastapi import FastAPI, Request
import os
from CapaDatos.ConvertirJson import ConvertirJson
from CapaDatos.InterpreteJson import InterpreteJson
from CapaNegocio.SellarXML import SellarXML
from CapaNegocio.ConfiguracionSello import ConfiguracionSello
from cryptography.fernet import Fernet

app = FastAPI()

@app.post("/InterpreteJson/")
async def procesar_json(request: Request):
    raw_body: str = await request.body()
    raw_body = raw_body.decode("utf-8")

    try:
        interprete = InterpreteJson(raw_body)
    except ValueError as e:
        return {"error": str(e)}
    
    convertir = ConvertirJson(interprete.jsonData)
    xml_generado = convertir.GenerarXmlCFDI()

    # Generar cadena original
    try:
        # Cargar clave Fernet del archivo env
        env_path = os.path.join(os.path.dirname(__file__), 'FernetKey.env')
        fernet_key = None
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('FERNET_KEY'):
                        # Formato: FERNET_KEY = valor
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            fernet_key = parts[1].strip().strip()
                            # limpiar formato base64
                            fernet_key = fernet_key.strip().strip('"').strip("'")
                        break
        if not fernet_key:
            # En caso de no encontrar key, generar temporal (solo para evitar crash)
            fernet_key = Fernet.generate_key().decode()

        configuracion = ConfiguracionSello(raw_body, fernet_key.encode())
        sellador = SellarXML(1, configuracion, xml_generado)
        cadena_original = sellador.generarCadenaOriginal(convertir)
    except Exception as e:
        cadena_original = None

    # Firmar la cadena con private key
    sello = None
    try:
        if cadena_original:
            sello = sellador.GenerarSello(cadena_original)
    except Exception as e:
        sello = f"ERROR_SIGN: {e}"


    # Visualización de resultado en post
    conceptos_formato = [
        f"Desc: {c.get('descripcion')} - Cant: {c.get('cantidad')} - Precio: {c.get('precioUnitario')}"
        for c in interprete.conceptos
    ]

    # Atributos a mostrar en resultado post
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
    "xml": xml_generado,
    "cadena_original": cadena_original,
    "sello": sello,
    "xml_con_sello": sellador.agregarSelloAlXML(sello) if sello else None
    }