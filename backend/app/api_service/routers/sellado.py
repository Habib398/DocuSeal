"""
Router de Sellado - Endpoints para sellado de CFDI

Este módulo contiene los endpoints relacionados con el sellado de CFDI,
delegando toda la lógica de negocio a ServicioSellado y ServicioTimbrarSellar.
"""
import sys
import os
import logging
import xml.etree.ElementTree as ET

from fastapi import APIRouter, Body

# Añadir ruta del backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from Business.Services.ServicioSellado import ServicioSellado
from Business.Services.ServicioTimbrarSellar import ServicioTimbrarSellar
from Business.cfdi.ComprobanteFactory import ComprobanteFactory
from Business.Configuration.ConfiguracionCorreo import ConfiguracionCorreo
from Business.Configuration.ConfiguracionMensajes import ConfiguracionMensajes
from Business.Correo import Correo

logger = logging.getLogger(__name__)

# Crear router sin tags globales para poder asignar tags específicos a cada endpoint
router = APIRouter(
    prefix=""
)




def enviar_correo_timbrado(resultado: dict, datos_entrada: dict):
    """
    Función auxiliar para enviar correo después del timbrado completo.
    Solo se usa en /timbrarSellar/ que hace timbrado completo.
    
    Adjunta el XML timbrado y PDF (si está disponible) al correo.
    No bloquea la respuesta si falla el envío.
    """
    try:
        # Verificar si se solicitó correo
        solicito_correo = datos_entrada.get('solicito_correo', False)
        destinatarios = datos_entrada.get('destinatarios', [])
        
        # Si no se solicitó correo o no hay destinatarios, salir
        if not solicito_correo or not destinatarios:
            return None
        
        # Verificar que el timbrado fue exitoso (no tiene 'errores')
        if 'errores' in resultado:
            logger.info("Timbrado no exitoso, no se envía correo")
            return None
        
        # Extraer datos del comprobante para personalizar el mensaje
        tipo_comprobante = None
        folio = None
        
        # Intentar extraer del datosXML primero
        datos_xml = datos_entrada.get('datosXML', {})
        if isinstance(datos_xml, dict):
            comprobante = datos_xml.get('cfdi:Comprobante', {})
            tipo_comprobante = comprobante.get('TipoDeComprobante')
            folio = comprobante.get('Folio')
        
        # Si no se encontró en datosXML, intentar extraer del XML string
        if not tipo_comprobante and 'xml' in datos_entrada:
            try:
                xml_string = datos_entrada.get('xml', '')
                root = ET.fromstring(xml_string)
                
                # Obtener TipoDeComprobante
                tipo_comprobante = root.get('TipoDeComprobante')
                
                # Obtener Folio
                folio = root.get('Folio')
                
                if tipo_comprobante:
                    logger.info(f"Datos extraídos del XML: tipo={tipo_comprobante}, folio={folio}")
            except Exception as e:
                logger.warning(f"Error al parsear XML para extraer datos: {e}")
        
        # Obtener UUID del timbrado
        uuid_timbrado = resultado.get('uuid', '')
        
        # Generar asunto y cuerpo personalizados con los datos del comprobante
        asunto = ConfiguracionMensajes.obtener_asunto_timbrado(tipo_comprobante)
        cuerpo = ConfiguracionMensajes.obtener_cuerpo_timbrado(
            tipo_comprobante=tipo_comprobante,
            folio=folio
        )
        
        # Obtener XML timbrado (para adjuntar)
        xml_content = None
        xml_string = resultado.get('cuerpo')
        if xml_string:
            xml_content = xml_string.encode('utf-8')
        
        # Obtener PDF (si está disponible)
        pdf_bytes = None
        # El PDF viene como 'pdf_base64' en la respuesta del servicio
        pdf_base64 = resultado.get('pdf_base64')
        if pdf_base64:
            # Viene en base64, decodificar a bytes
            import base64
            try:
                pdf_bytes = base64.b64decode(pdf_base64)
                logger.info("PDF decodificado desde base64")
            except Exception as e:
                logger.warning(f"Error al decodificar PDF base64: {e}")
                pdf_bytes = None
        
        logger.info(f"Iniciando envío de correo a {len(destinatarios)} destinatario(s) con adjuntos")
        
        # Crear instancia de Correo y enviar CON ADJUNTOS
        config = ConfiguracionCorreo()
        correo = Correo(config)
        
        # EnviarCorreo ahora soporta xml_content, pdf_bytes y uuid
        resultado_correo = correo.EnviarCorreo(
            para=destinatarios,
            asunto=asunto,
            cuerpo=cuerpo,
            solicito_correo=True,
            timbrado_exitoso=True,
            xml_content=xml_content,
            pdf_bytes=pdf_bytes,
            uuid=uuid_timbrado
        )
        
        logger.info(f"Resultado de envío de correo: {resultado_correo['exitoso']}")
        return resultado_correo
        
    except Exception as e:
        # No afectar la respuesta de timbrado si falla el correo
        logger.error(f"Error al enviar correo después del timbrado: {str(e)}")
        return {
            'exitoso': False,
            'mensaje': 'Error al enviar correo',
            'error': str(e)
        }


@router.post(
    "/sellar/",
    summary="Sellar CFDI",
    description="Sellado de un CFDI. Acepta 'xml' (string XML) o 'datosXML' (estructura JSON con cfdi:Comprobante). Requiere 'claveUsuario'.",
    tags=["Sellado"]
)
async def sellar_endpoint(
    data: dict = Body(
        ...,
        description="Objeto JSON con 'xml' (string XML) o 'datosXML' (estructura JSON del comprobante) y 'claveUsuario'.",
        example={
            "datosXML(JSON) o xml(String xml)": "",
            "claveUsuario": "550e8400-e29b-41d4-a716-446655440000",
            "generarPDF": False
        }
    )
):
    # Procesar comprobante si se envía datosXML
    if "datosXML" in data:
        resultado = ComprobanteFactory.procesar_comprobante(data["datosXML"])
        if not resultado["valido"]:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "mensaje": "Errores de validación en el comprobante",
                    "errores": resultado["errores"],
                    "warnings": resultado["warnings"]
                }
            )
        # Reemplazar datosXML con el XML generado
        data["xml"] = resultado["xml"]
        del data["datosXML"]
    
    # NOTA: /sellar/ SOLO sella el comprobante, no timbra
    # Por lo tanto NO envía correo (no hay UUID ni PDF de timbrado)
    return ServicioSellado.sellar(data)


@router.post(
    "/timbrarSellar/",
    summary="Sellar y timbrar CFDI",
    description="Realiza el sellado y timbrado completo. Acepta 'xml' (string XML) o 'datosXML' (estructura JSON con cfdi:Comprobante). "
                "Opcionalmente genera PDF y envía correo. Requiere 'claveUsuario' para obtener credenciales PAC.",
    tags=["Timbrado y Sellado"]
)
async def timbrar_sellar_endpoint(
    data: dict = Body(
        ...,
        description="JSON con 'xml' (string XML) o 'datosXML' (estructura JSON del comprobante) y 'claveUsuario'. "
                    "Las credenciales PAC se obtienen automáticamente. El modo de pruebas se toma del certificado.",
        example={
            "datosXML(JSON) o xml(String xml)": {},
            "claveUsuario": "550e8400-e29b-41d4-a716-446655440000",
            "generarPDF": False,
            "solicito_correo": False,
            "destinatarios": [],
            "asunto": "Comprobante Timbrado",
            "cuerpo": "Se adjunta su comprobante electrónico timbrado."
        }
    )
):
    # DEBUG
    import sys
    sys.stderr.flush()
    print(f"\n{'='*60}", file=sys.stderr, flush=True)
    print(f"=== ENDPOINT timbrar_sellar_endpoint CALLED ===", file=sys.stderr, flush=True)
    print(f"data keys: {list(data.keys())}", file=sys.stderr, flush=True)
    print(f"Has datosXML: {'datosXML' in data}", file=sys.stderr, flush=True)
    print(f"{'='*60}\n", file=sys.stderr, flush=True)
    sys.stderr.flush()
    
    # Procesar comprobante si se envía datosXML
    if "datosXML" in data:
        resultado = ComprobanteFactory.procesar_comprobante(data["datosXML"])
        if not resultado["valido"]:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "mensaje": "Errores de validación en el comprobante",
                    "errores": resultado["errores"],
                    "warnings": resultado["warnings"]
                }
            )
        # Guardar datosXML para usar en el correo antes de reemplazarlo
        datos_xml_guardado = data["datosXML"]
        # Reemplazar datosXML con el XML generado
        data["xml"] = resultado["xml"]
        del data["datosXML"]
    else:
        datos_xml_guardado = None
    
    # Realizar timbrado y sellado
    resultado = ServicioTimbrarSellar.procesar(data)
    
    # Si el timbrado fue exitoso (no tiene errores), intentar enviar correo
    # Nota: ServicioTimbrarSellar devuelve {'errores': [...]} si hay error
    #       o un dict sin 'errores' si es exitoso
    if 'errores' not in resultado:
        # Restaurar datosXML en data para que enviar_correo_timbrado pueda acceder
        if datos_xml_guardado:
            data["datosXML"] = datos_xml_guardado
        resultado_correo = enviar_correo_timbrado(resultado, data)
        if resultado_correo:
            resultado['correo'] = resultado_correo
    
    return resultado
