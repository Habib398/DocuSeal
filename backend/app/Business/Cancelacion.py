"""
Cancelacion.py - Business Logic para operaciones de cancelación de CFDI.

NOTA: Este archivo mantiene compatibilidad con código existente.
La implementación real está en el paquete CancelacionPACs/.

Para soporte multi-PAC futuro, usar:
- CancelacionPACs.CancelacionComercioDigital para Comercio Digital
- CancelacionPACs.CancelacionGenericaPAC para otros PACs
"""

import logging
from typing import Dict, Any, Optional

from .ResultadoCancelacion import ResultadoCancelacion
from .CancelacionPACs.CancelacionComercioDigital import CancelacionComercioDigital

logger = logging.getLogger(__name__)

class CancelacionService:
    """
    Servicio para cancelar CFDI.
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
        Cancela un UUID de CFDI.
        
        """
        # Crear instancia de la implementación de Comercio Digital
        cancelador = CancelacionComercioDigital()
        
        # Preparar kwargs con todos los parámetros
        kwargs = {
            'rfc_receptor': rfc_receptor,
            'total': total,
            'tipo_comprobante': tipo_comprobante,
            'motivo': motivo,
            'certificado_base64': certificado_base64,
            'key_base64': key_base64,
            'password_key': password_key,
            'rfc_emisor': rfc_emisor,
            'uuid_relacionado': uuid_relacionado,
            'email_emisor': email_emisor,
            'email_receptor': email_receptor,
            'guardar_acuse': guardar_acuse
        }
        
        # Delegar a la implementación
        return cancelador.cancelar(
            folio_fiscal=uuid,
            usuario=usuario_pac,
            password=password_pac,
            pruebas=pruebas,
            **kwargs
        )


# Instancia del servicio para uso directo
cancelacion_service = CancelacionService()
