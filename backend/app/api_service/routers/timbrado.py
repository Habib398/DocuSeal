"""
Router de Timbrado - Endpoints para timbrado de CFDI

Este módulo contiene los endpoints relacionados con el timbrado de CFDI,
delegando toda la lógica de negocio a ServicioTimbrado.
"""

from fastapi import APIRouter, Body
import sys
import os
import logging

# Añadir ruta del backend al path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from Business.Services.ServicioTimbrado import ServicioTimbrado
from Business.Configuration.ConfiguracionCorreo import ConfiguracionCorreo
from Business.Correo import Correo

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="",
    tags=["Timbrado"]
)


def enviar_correo_timbrado(resultado_timbrado: dict, datos_entrada: dict):
    """
    Función auxiliar para enviar correo después del timbrado completo.
    Solo se usa en endpoints que realizan TIMBRADO (generan UUID y PDF).
    """
    try:
        # Verificar si se solicitó correo y si el timbrado fue exitoso
        solicito_correo = datos_entrada.get('solicito_correo', False)
        destinatarios = datos_entrada.get('destinatarios', [])
        
        # Si no se solicitó correo o no hay destinatarios, salir
        if not solicito_correo or not destinatarios:
            return None
        
        # Verificar que el timbrado fue exitoso (no tiene 'errores')
        if 'errores' in resultado_timbrado:
            logger.info("Timbrado no exitoso, no se envía correo")
            return None
        
        # Obtener asunto y cuerpo, con valores por defecto
        asunto = datos_entrada.get('asunto', 'Comprobante Timbrado')
        cuerpo = datos_entrada.get('cuerpo', 'Se adjunta su comprobante electrónico timbrado.')
        
        # Obtener UUID del timbrado para incluir en el correo
        uuid_timbrado = resultado_timbrado.get('uuid', '')
        if uuid_timbrado:
            cuerpo = f"{cuerpo}\n\nUUID del timbrado: {uuid_timbrado}"
        
        # Obtener XML timbrado (para adjuntar)
        xml_content = None
        xml_string = resultado_timbrado.get('cuerpo')
        if xml_string:
            xml_content = xml_string.encode('utf-8')
        
        # Obtener PDF (si está disponible)
        pdf_bytes = None
        # El PDF viene como 'pdf_base64' en la respuesta del servicio
        pdf_base64 = resultado_timbrado.get('pdf_base64')
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
        
        # EnviarCorreo ahora soporta xml_content y pdf_bytes
        resultado_correo = correo.EnviarCorreo(
            para=destinatarios,
            asunto=asunto,
            cuerpo=cuerpo,
            solicito_correo=True,
            timbrado_exitoso=True,
            xml_content=xml_content,
            pdf_bytes=pdf_bytes
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

@router.post("/timbrar/",
    summary="Timbrar CFDI",
    description="Timbrado de un XML de CFDI previamente sellado. Se requiere claveUsuario para identificar el certificado. Opcionalmente genera PDF."
)
async def timbrar_endpoint(
    data: dict = Body(
        ...,
        description="Objeto JSON con 'xml' (string XML sellado completo), 'claveUsuario' para identificar el certificado, y 'generarPDF' (opcional). El modo de pruebas se toma del certificado.",
        example={
            "xml": "",
            "claveUsuario": "550e8400-e29b-41d4-a716-446655440000",
            "generarPDF": False,
            "solicito_correo": False,
            "destinatarios": [],
            "asunto": "Comprobante Timbrado",
            "cuerpo": "Se adjunta su comprobante electrónico timbrado."
        }
    )
):
    
    # Realizar timbrado
    resultado = ServicioTimbrado.timbrar(data)
    
    # Si el timbrado fue exitoso (no tiene errores), intentar enviar correo
    # Nota: ServicioTimbrado devuelve {'errores': [...]} si hay error
    #       o un dict sin 'errores' si es exitoso
    if 'errores' not in resultado:
        resultado_correo = enviar_correo_timbrado(resultado, data)
        if resultado_correo:
            resultado['correo'] = resultado_correo
    
    return resultado
