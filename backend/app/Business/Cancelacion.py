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
        rfc_emisor: Optional[str] = None,
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
                url = "https://pruebas.comercio-digital.mx/cancela4/cancelarUuid"
            else:
                url = "https://cancela.comercio-digital.mx/cancela4/cancelarUuid"
            
            logger.info(f"Cancelando UUID {uuid} en ambiente {'PRUEBAS' if pruebas else 'PRODUCCIÓN'}")
            logger.info(f"URL: {url}")
            
            # Extraer RFC emisor del certificado si no se proporcionó
            if not rfc_emisor:
                try:
                    from satcfdi.models import Signer
                    import base64 as b64
                    
                    cert_bytes = b64.b64decode(certificado_base64)
                    key_bytes = b64.b64decode(key_base64)
                    
                    signer = Signer.load(
                        certificate=cert_bytes,
                        key=key_bytes,
                        password=password_key
                    )
                    rfc_emisor = signer.rfc
                    logger.info(f"RFC emisor extraído del certificado: {rfc_emisor}")
                except Exception as e:
                    logger.warning(f"Error al extraer RFC del certificado: {e}")
            
            # Preparar headers básicos
            headers = {
                "Content-Type": "text/plain"
            }
            
            # Construir el body según formato de Comercio Digital
            # Todo va en el body como pares PARAMETRO=valor separados por saltos de línea
            body_parts = [
                f"USER={usuario_pac.replace('Ñ', '@')}",
                f"PWDW={password_pac}",
                f"TIPO1=cfdi",
                f"UUID={uuid}",
                f"RFCR={rfc_receptor}",
                f"TOTAL={total}",
                f"TIPOC={tipo_comprobante}",
                f"MOTIVO={motivo}",
                f"PWDK={password_key}"
            ]
            
            # Agregar RFC emisor si está disponible
            if rfc_emisor:
                body_parts.append(f"RFCE={rfc_emisor}")
            
            # Agregar email emisor si está presente (opcional)
            if email_emisor:
                body_parts.append(f"EMAILE={email_emisor}")
            
            # Agregar email receptor si está presente (opcional)
            if email_receptor:
                body_parts.append(f"EMAILR={email_receptor}")
            
            # Agregar UUID relacionado solo si el motivo es 01
            if motivo == "01" and uuid_relacionado:
                body_parts.append(f"UUIDREL={uuid_relacionado}")
            
            # Agregar opción de guardar acuse
            if guardar_acuse:
                body_parts.append("ACUS=SI")
            else:
                body_parts.append("ACUS=NO")
            
            # Agregar certificados en Base64 al final
            body_parts.append(f"KEYF={key_base64}")
            body_parts.append(f"CERT={certificado_base64}")
            
            # Unir todas las partes con saltos de línea
            body = "\n".join(body_parts)
            
            logger.info(f"Enviando solicitud de cancelación al PAC para UUID: {uuid}")
            logger.info(f"Body parameters: USER, PWDW, TIPO1, UUID, RFCR, TOTAL, TIPOC, MOTIVO, PWDK, RFCE, KEYF, CERT")
            logger.info(f"Body length: {len(body)}")
            
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
