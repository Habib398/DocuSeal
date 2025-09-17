from fastapi import FastAPI, Request
import os
from CapaDatos.ConvertirJson import ConvertirJson
from CapaDatos.InterpreteJson import InterpreteJson
from CapaNegocio.SellarXML import SellarXML
from CapaNegocio.ConfiguracionSello import ConfiguracionSello
from cryptography.fernet import Fernet
from CapaNegocio.Timbrado import timbrado_service
from CapaNegocio.ValidadorCFDI import ValidadorCFDI

app = FastAPI()

@app.post("/InterpreteJson/")
async def procesar_json(request: Request):
    raw_body: str = await request.body()
    raw_body = raw_body.decode("utf-8")

    interprete = InterpreteJson(raw_body)
    convertir = ConvertirJson(interprete.jsonData)
    validador = ValidadorCFDI(interprete.jsonData)
    validaciones = validador.ejecutar()
    xml_generado = convertir.GenerarXmlCFDI()

    # Cargar clave Fernet del archivo env para desencriptar (Hecho por Copilot)
    env_path = os.path.join(os.path.dirname(__file__), 'FernetKey.env')
    fernet_key = None
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line.startswith('FERNET_KEY'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        fernet_key = parts[1].strip().strip()
                        fernet_key = fernet_key.strip().strip('"').strip("'")
                    break
    if not fernet_key:
        fernet_key = Fernet.generate_key().decode()

    configuracion = ConfiguracionSello(raw_body, fernet_key.encode())
    sellador = SellarXML(1, configuracion, xml_generado)
    cadena_original = sellador.generarCadenaOriginal(convertir)

    # Firmar la cadena con private key (.key/.cer manejo básico)
    sello = None
    try:
        if cadena_original:
            sello = sellador.GenerarSello(cadena_original)
    except Exception as e:
        sello = f"ERROR_SIGN: {e}"

    conceptos_formato = [
        f"Desc: {c.get('descripcion')} - Cant: {c.get('cantidad')} - Precio: {c.get('precioUnitario')}"
        for c in interprete.conceptos
    ]

    resultado = {
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
        "validaciones_pre": validaciones,
        "cadena_original": cadena_original,
        "sello": sello,
        "xml_con_sello": sellador.agregarSelloAlXML(sello) if sello else None,
    }

    # Validar el XML contra el XSD después de agregar el sello
    try:
        from CapaNegocio.ValidadorXMLCFDI import ValidadorXMLCFDI
        xsd_path = "CapaDatos/cfdv40.xsd"  # Ajusta la ruta si tu XSD está en otro lugar
        if resultado["xml_con_sello"]:
            validacion_xml = ValidadorXMLCFDI.validar_xml(resultado["xml_con_sello"], xsd_path)
            resultado["xml_valido_xsd"] = validacion_xml["valido"]
            resultado["xml_errores_xsd"] = validacion_xml["errores"]
    except Exception as e:
        resultado["xml_valido_xsd"] = False
        resultado["xml_errores_xsd"] = [str(e)]

        # Verificar el sello digital antes de timbrar
    try:
        from CapaNegocio.VerificadorSello import VerificadorSello
        sello_valido = False
        if cadena_original and sello and interprete.cer:
            sello_valido = VerificadorSello.verificar_sello(cadena_original, sello, interprete.cer)
        resultado["sello_valido"] = sello_valido
    except Exception as e:
        resultado["sello_valido"] = False
        resultado["error_verificacion_sello"] = str(e)

    try:
        if resultado.get("xml_con_sello") and interprete.usuario_pac and interprete.contrasena_pac:
            timb = timbrado_service.timbrar(
                resultado["xml_con_sello"],
                interprete.usuario_pac,
                interprete.contrasena_pac,
                pruebas=True,
            )
            mensaje_detallado = timb.get("errmsg") or timb.get("mensaje")
            resultado.update({
                "timbrado_codigo": timb.get("codigo"),
                "timbrado_mensaje": mensaje_detallado,
                "uuid": timb.get("uuid"),
                "xml_timbrado": timb.get("cuerpo"),
            })
    except Exception as e:
        resultado.update({
            "timbrado_codigo": -99,
            "timbrado_mensaje": f"Fallo inesperado al timbrar: {e}",
        })

    return resultado