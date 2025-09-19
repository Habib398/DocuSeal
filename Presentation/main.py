from fastapi import FastAPI, Request
import json
import os
import re
from Data.ConvertirJson import ConvertirJson
from Business.SellarXML import SellarXML
from Business.ConfiguracionSello import ConfiguracionSello
from cryptography.fernet import Fernet
from Business.Timbrado import timbrado_service
from fastapi import Body


app = FastAPI()
@app.post("/timbrar/")
async def timbrar_endpoint(
    xml: str = Body(..., embed=True),
    usuario_pac: str = Body(..., embed=True),
    contrasena_pac: str = Body(..., embed=True),
    pruebas: bool = Body(True, embed=True)
):
    xml_limpio = re.sub(r"<\?xml[^>]*encoding=['\"]?utf-8['\"]?[^>]*\?>", "", xml, flags=re.IGNORECASE)
    xml_limpio = xml_limpio.strip()
    resultado = timbrado_service.timbrar(
        xml=xml_limpio,
        usuario_pac=usuario_pac,
        contrasena_pac=contrasena_pac,
        pruebas=pruebas
    )
    return resultado

@app.post("/sellar/")
async def sellar_endpoint(data: dict = Body(...)):
    # Obtener la clave Fernet
    env_path = os.path.join(os.path.dirname(__file__), 'FernetKey.env')
    fernet_key = None
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line.startswith('FERNET_KEY'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        fernet_key = parts[1].strip().strip('"').strip("'")
                    break
    if not fernet_key:
        fernet_key = Fernet.generate_key().decode()

    # Configuración y sellado
    raw_body = json.dumps(data)
    configuracion = ConfiguracionSello(raw_body, fernet_key.encode())
    convertir = ConvertirJson(data["datos_xml"])
    xml_generado = convertir.GenerarXmlCFDI()
    sellador = SellarXML(1, configuracion, xml_generado)


    try:
        xml_con_sello = sellador.GenerarSello(convertir)
    except Exception as e:
        return {"error": str(e)}
    return {"xml_con_sello": xml_con_sello}


@app.post("/timbrarSellar/")
async def timbrar_sellar_endpoint(
    data: dict = Body(...)
):
    env_path = os.path.join(os.path.dirname(__file__), 'FernetKey.env')
    fernet_key = None
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line.startswith('FERNET_KEY'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        fernet_key = parts[1].strip().strip('"').strip("'")
                    break
    if not fernet_key:
        fernet_key = Fernet.generate_key().decode()


    # Sellado: aceptar diccionario o string XML
    raw_body = json.dumps(data)
    configuracion = ConfiguracionSello(raw_body, fernet_key.encode())
    datos_xml = data.get("datos_xml")
    if datos_xml is None:
        return {"error": "Falta el campo 'datos_xml'"}

    # Si es dict, usar ConvertirJson; si es str, usar directamente
    if isinstance(datos_xml, dict):
        convertir = ConvertirJson(datos_xml)
        xml_generado = convertir.GenerarXmlCFDI()
        sellador = SellarXML(1, configuracion, xml_generado)
        try:
            xml_con_sello = sellador.GenerarSello(convertir)
        except Exception as e:
            return {"error": f"Error al sellar: {str(e)}"}
    elif isinstance(datos_xml, str):
        sellador = SellarXML(1, configuracion, datos_xml)
        try:
            xml_con_sello = sellador.GenerarSello()
        except Exception as e:
            return {"error": f"Error al sellar: {str(e)}"}
    else:
        return {"error": "El campo 'datos_xml' debe ser un diccionario o un string XML."}

    # Timbrado
    usuario_pac = data.get("PAC", {}).get("usuario")
    contrasena_pac = data.get("PAC", {}).get("contrasena")
    pruebas = data.get("pruebas", True)
    if not usuario_pac or not contrasena_pac:
        return {"error": "Faltan credenciales PAC (objeto PAC incompleto o vacío)"}

    # Eliminar declaración de encoding si existe (Hecho por Copilot)
    if isinstance(xml_con_sello, str):
        xml_con_sello = re.sub(r'<\?xml[^>]*\?>', '', xml_con_sello).strip()
    try:
        resultado_timbrado = timbrado_service.timbrar(
            xml=xml_con_sello,
            usuario_pac=usuario_pac,
            contrasena_pac=contrasena_pac,
            pruebas=pruebas
        )
    except Exception as e:
        return {"error": f"Error al timbrar: {str(e)}"}

    return resultado_timbrado