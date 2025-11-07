"""
Cancelacion.py - Business Logic para operaciones de cancelación de CFDI.
Implementación directa del Web Service de Comercio Digital.
"""

import logging
import base64
import requests
from typing import Dict, Any, Optional
from xml.etree import ElementTree as ET

from .ResultadoCancelacion import ResultadoCancelacion

logger = logging.getLogger(__name__)

class CancelacionService:
    """
    Servicio para cancelar CFDI utilizando el Web Service directo de Comercio Digital.
    """
    
    # Motivos válidos de cancelación
    MOTIVOS_VALIDOS = ["01", "02", "03", "04"]
    
    @classmethod
    def cancelar_uuid(
        cls,
        uuid: str,
        rfc_receptor: str,
        total: str,
        tipo_comprobante: str,
        motivo: str,
        usuario_pac: str,
        password_pac: str,
        certificado_base64: str,
        key_base64: str,
        password_key: str,
        uuid_relacionado: Optional[str] = None,
        email_emisor: Optional[str] = None,
        email_receptor: Optional[str] = None,
        guardar_acuse: bool = True,
        pruebas: bool = True
    ) -> Dict[str, Any]:
        """
        Cancela un UUID de CFDI mediante el Web Service de Comercio Digital.
        Implementación directa según documentación oficial del PAC.
        """
        
        try:
            # Validar motivo y UUID relacionado
            if motivo not in cls.MOTIVOS_VALIDOS:
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    "Motivo inválido",
                    f"El motivo debe ser uno de: 01, 02, 03, 04. Recibido: {motivo}"
                )
            
            if motivo == "01" and not uuid_relacionado:
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    "UUID relacionado requerido",
                    "El motivo '01' requiere especificar 'uuid_relacionado'"
                )
            
            # Determinar URL según ambiente
            if pruebas:
                base_url = "https://pruebas.comercio-digital.mx"
            else:
                base_url = "https://cancela.comercio-digital.mx"
            
            # URL del endpoint de cancelación
            url = f"{base_url}/cancela4/cancelarUuid"
            
            logger.info(f"Cancelando UUID {uuid} en ambiente {'PRUEBAS' if pruebas else 'PRODUCCIÓN'}")
            logger.info(f"URL: {url}")
            
            # Preparar headers según documentación de Comercio Digital
            headers = {
                "USER": usuario_pac.replace('Ñ', '@'),  # Comercio Digital usa @ en lugar de Ñ
                "PWDW": password_pac,
                "TIPO1": "cfdi",  # Tipo de documento (cfdi o reten)
                "UUID": uuid,  # UUID del comprobante a cancelar
                "RFCR": rfc_receptor,
                "TOTAL": str(total),
                "TIPOC": tipo_comprobante,
                "MOTIVO": motivo,
                "PWDK": password_key,
                "Content-Type": "text/plain"  # Comercio Digital requiere text/plain
            }
            
            # Agregar email emisor si está presente (opcional)
            if email_emisor:
                headers["EMAILE"] = email_emisor
            
            # Agregar email receptor si está presente (opcional)
            if email_receptor:
                headers["EMAILR"] = email_receptor
            
            # Agregar UUID relacionado solo si el motivo es 01
            if motivo == "01" and uuid_relacionado:
                headers["UUIDREL"] = uuid_relacionado
            
            # Agregar opción de guardar acuse
            if guardar_acuse:
                headers["ACUS"] = "SI"
            else:
                headers["ACUS"] = "NO"
            
            # Preparar body con certificados en Base64
            # El UUID va en la URL, los certificados en el body como texto plano
            body = f"{key_base64}|{certificado_base64}"
            
            logger.info(f"Enviando solicitud de cancelación al PAC para UUID: {uuid}")
            logger.debug(f"Headers (sin contraseñas): USER={usuario_pac}, RFCR={rfc_receptor}, TOTAL={total}, TIPOC={tipo_comprobante}, MOTIVO={motivo}")
            
            # Realizar petición HTTP al PAC
            response = requests.post(
                url=url,
                headers=headers,
                data=body,
                timeout=30
            )
            
            logger.info(f"Respuesta del PAC - Status Code: {response.status_code}")
            
            # Verificar respuesta exitosa
            if response.status_code == 200:
                # Comercio Digital devuelve el código en headers
                codigo = response.headers.get('codigo', '')
                
                if codigo == '000':
                    logger.info(f"Cancelación exitosa para UUID: {uuid}")
                    
                    # Extraer acuse de la respuesta
                    acuse_data = {
                        "fecha": response.headers.get('fecha'),
                        "codigo": codigo,
                        "mensaje": response.headers.get('msg', 'Cancelación exitosa'),
                        "uuid": uuid,
                        "folios": [{
                            "uuid": uuid,
                            "estatus": "Cancelado"
                        }]
                    }
                    
                    # Si hay contenido XML en la respuesta, agregarlo
                    if response.content:
                        acuse_data["acuse_xml"] = response.content.decode('utf-8', errors='ignore')
                    
                    return ResultadoCancelacion.ResultadoExito(uuid, acuse_data)
                else:
                    # El PAC devolvió un código de error
                    error_msg = response.headers.get('errmsg', 'Error desconocido del PAC')
                    logger.error(f"PAC rechazó cancelación. Código: {codigo}, Mensaje: {error_msg}")
                    
                    return ResultadoCancelacion.ResultadoError(
                        uuid,
                        f"Error del PAC (código {codigo})",
                        error_msg
                    )
            else:
                # Error HTTP
                error_msg = f"Error HTTP {response.status_code}"
                detalle = response.text if response.text else "Sin detalles adicionales"
                
                logger.error(f"Error HTTP al cancelar UUID {uuid}: {error_msg}")
                logger.error(f"Respuesta: {detalle}")
                
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    error_msg,
                    detalle
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al cancelar UUID {uuid}")
            return ResultadoCancelacion.ResultadoError(
                uuid,
                "Timeout de conexión con el PAC",
                "La solicitud excedió el tiempo de espera de 30 segundos"
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión al cancelar UUID {uuid}: {str(e)}")
            return ResultadoCancelacion.ResultadoError(
                uuid,
                "Error de conexión con el PAC",
                str(e)
            )
            
        except Exception as e:
            logger.exception(f"Error inesperado al cancelar UUID {uuid}")
            return ResultadoCancelacion.ResultadoError(
                uuid,
                "Error inesperado en la cancelación",
                str(e)
            )


# Instancia del servicio para uso directo
cancelacion_service = CancelacionService()
