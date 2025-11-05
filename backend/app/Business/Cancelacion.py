"""
Cancelacion.py - Business Logic para operaciones de cancelación de CFDI.
"""

import logging
import base64
from typing import Dict, Any, Optional
from datetime import datetime
from satcfdi.pacs.comerciodigital import ComercioDigital
from satcfdi.pacs import Environment, CancelReason
from satcfdi.models import Signer
from satcfdi.create.cancela.cancelacion import Cancelacion, Folio

from .ResultadoCancelacion import ResultadoCancelacion

logger = logging.getLogger(__name__)

class CancelacionService:
    """
    Servicio para cancelar CFDI utilizando satcfdi y el PAC Comercio Digital.
    """
    
    # Mapeo de motivos numéricos a CancelReason
    MOTIVOS_MAP = {
        "01": CancelReason.COMPROBANTE_EMITIDO_CON_ERRORES_CON_RELACION,
        "02": CancelReason.COMPROBANTE_EMITIDO_CON_ERRORES_SIN_RELACION,
        "03": CancelReason.NO_SE_LLEVO_A_CABO_LA_OPERACION,
        "04": CancelReason.OPERACION_NORMATIVA_RELACIONADA_EN_LA_FACTURA_GLOBAL
    }
    
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
        Cancela un UUID de CFDI mediante satcfdi y el PAC Comercio Digital.
        """
        
        try:
            # Validar motivo y UUID relacionado
            if motivo not in cls.MOTIVOS_MAP:
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
            
            # Decodificar certificados de Base64
            try:
                cert_data = base64.b64decode(certificado_base64)
                key_data = base64.b64decode(key_base64)
            except Exception as e:
                logger.error(f"Error al decodificar certificados: {e}")
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    "Error al decodificar certificados",
                    f"Los certificados deben estar en formato Base64 válido: {str(e)}"
                )
            
            # Crear Signer con certificados
            try:
                signer = Signer.load(
                    certificate=cert_data,
                    key=key_data,
                    password=password_key
                )
                logger.info(f"Signer creado correctamente. RFC: {signer.rfc}")
            except Exception as e:
                logger.error(f"Error al crear Signer: {e}")
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    "Error al procesar certificados",
                    f"No se pudo crear el Signer con los certificados proporcionados: {str(e)}"
                )
            
            # Objeto folio
            folio = Folio(
                uuid=uuid,
                motivo=motivo,
                folio_sustitucion=uuid_relacionado if motivo == "01" else None
            )
            
            # solicitud de cancelación usando folios
            try:
                cancelacion = Cancelacion(
                    emisor=signer,
                    folios=[folio],
                    fecha=datetime.now()
                )
            except Exception as e:
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    "Error al crear solicitud de cancelación",
                    str(e)
                )
            
            # Configurar ambiente del PAC
            env = Environment.TEST if pruebas else Environment.PRODUCTION
            
            # Crear cliente del PAC
            try:
                pac = ComercioDigital(
                    user=usuario_pac,
                    password=password_pac,
                    environment=env
                )
            except Exception as e:
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    "Error al configurar cliente PAC",
                    str(e)
                )
            
            # Enviar solicitud de cancelación al PAC
            try:
                logger.info(f"Enviando solicitud de cancelación al PAC para UUID: {uuid}")
                acuse = pac.cancel_comprobante(cancelacion)
                logger.info(f"Cancelación exitosa para UUID: {uuid}")
                                
                # Preparar datos del acuse para respuesta
                acuse_data = {
                    "fecha": str(acuse.fecha) if hasattr(acuse, 'fecha') else None,
                    "folios": []
                }
                
                # Extraer información de los folios del acuse
                if hasattr(acuse, 'folios'):
                    for folio_acuse in acuse.folios:
                        folio_info = {
                            "uuid": folio_acuse.uuid if hasattr(folio_acuse, 'uuid') else None,
                            "estatus": folio_acuse.estatus if hasattr(folio_acuse, 'estatus') else None
                        }
                        acuse_data["folios"].append(folio_info)
                
                return ResultadoCancelacion.ResultadoExito(uuid, acuse_data)
                
            except Exception as e:                
                # Extraer información del error
                error_msg = str(e) if str(e) else "Error desconocido del PAC"
                detalle = None
                logger.error(f"Error del PAC al cancelar UUID {uuid}: {error_msg}")
                
                # Intentar obtener más detalles si es un error HTTP
                if hasattr(e, 'response'):
                    response = e.response
                    if hasattr(response, 'text'):
                        detalle = response.text
                        logger.error(f"Respuesta del PAC: {detalle}")
                    if hasattr(response, 'status_code'):
                        error_msg = f"Error del PAC (Status {response.status_code}): {error_msg}"
                        logger.error(f"Status code: {response.status_code}")
                
                # Si no hay mensaje de error, proporcionar uno genérico
                if not error_msg or error_msg == "Error desconocido del PAC":
                    error_msg = "El PAC rechazó la solicitud de cancelación. Verifique que los certificados coincidan con el CFDI original."
                
                return ResultadoCancelacion.ResultadoError(
                    uuid,
                    error_msg,
                    detalle or str(e)
                )
                
        except Exception as e:
            return ResultadoCancelacion.ResultadoError(
                uuid,
                "Error inesperado en la cancelación",
                str(e)
            )


# Instancia del servicio para uso directo
cancelacion_service = CancelacionService()
