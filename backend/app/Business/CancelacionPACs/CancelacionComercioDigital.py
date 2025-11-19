"""
CancelacionComercioDigital.py - Implementación de cancelación para Comercio Digital.
Implementación personalizada del Web Service de Comercio Digital.
"""

import logging
import base64
import requests
from typing import Dict, Any, Optional

from .CancelacionPAC import CancelacionPAC, CancelacionPACException
from Business.ResultadoCancelacion import ResultadoCancelacion

logger = logging.getLogger(__name__)


class CancelacionComercioDigital(CancelacionPAC):
    """
    Implementación de cancelación para el PAC Comercio Digital.
    
    Comercio Digital no tiene soporte nativo en satcfdi para cancelación,
    por lo que se implementa directamente mediante su Web Service.
    """
    
    # Motivos válidos de cancelación
    MOTIVOS_VALIDOS = ["01", "02", "03", "04"]
    
    def obtener_tipo_pac(self) -> str:
        """Retorna el identificador del PAC."""
        return "comerciodigital"
    
    def validar_parametros(
        self, 
        folio_fiscal: str, 
        usuario: str, 
        password: str,
        **kwargs
    ) -> tuple[bool, Optional[str]]:
        """
        Valida los parámetros antes de procesar la cancelación.
        
        Args:
            folio_fiscal: UUID del comprobante.
            usuario: Usuario del PAC.
            password: Contraseña del PAC.
            **kwargs: Parámetros adicionales (motivo, uuid_relacionado, etc.)
        
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        # Validar UUID
        if not folio_fiscal or len(folio_fiscal) != 36:
            return False, "UUID inválido"
        
        # Validar credenciales
        if not usuario or not password:
            return False, "Usuario y contraseña son requeridos"
        
        # Validar motivo
        motivo = kwargs.get('motivo', '')
        if motivo not in self.MOTIVOS_VALIDOS:
            return False, f"Motivo debe ser uno de: {', '.join(self.MOTIVOS_VALIDOS)}"
        
        # Validar UUID relacionado si motivo es 01
        if motivo == "01" and not kwargs.get('uuid_relacionado'):
            return False, "UUID relacionado es requerido para motivo '01'"
        
        return True, None
    
    def cancelar(
        self, 
        folio_fiscal: str, 
        usuario: str, 
        password: str, 
        pruebas: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Cancela un CFDI mediante el Web Service de Comercio Digital.
        
        Args:
            folio_fiscal: UUID del comprobante a cancelar.
            usuario: Usuario del PAC.
            password: Contraseña del PAC.
            pruebas: Si es ambiente de pruebas.
            **kwargs: Parámetros adicionales:
                - rfc_receptor (str): RFC del receptor
                - total (str): Total del comprobante
                - tipo_comprobante (str): Tipo de comprobante
                - motivo (str): Motivo de cancelación (01-04)
                - certificado_base64 (str): Certificado en base64
                - key_base64 (str): Llave privada en base64
                - password_key (str): Contraseña de la llave
                - rfc_emisor (Optional[str]): RFC del emisor
                - uuid_relacionado (Optional[str]): UUID relacionado
                - email_emisor (Optional[str]): Email del emisor
                - email_receptor (Optional[str]): Email del receptor
                - guardar_acuse (bool): Si guardar acuse
        
        Returns:
            Dict con resultado de la cancelación
        """
        # Validar parámetros
        es_valido, error_msg = self.validar_parametros(folio_fiscal, usuario, password, **kwargs)
        if not es_valido:
            return ResultadoCancelacion.ResultadoError(
                folio_fiscal,
                "Parámetros inválidos",
                error_msg
            )
        
        try:
            # Extraer parámetros requeridos
            rfc_receptor = kwargs.get('rfc_receptor')
            total = kwargs.get('total')
            tipo_comprobante = kwargs.get('tipo_comprobante')
            motivo = kwargs.get('motivo')
            certificado_base64 = kwargs.get('certificado_base64')
            key_base64 = kwargs.get('key_base64')
            password_key = kwargs.get('password_key')
            
            # Parámetros opcionales
            rfc_emisor = kwargs.get('rfc_emisor')
            uuid_relacionado = kwargs.get('uuid_relacionado')
            email_emisor = kwargs.get('email_emisor')
            email_receptor = kwargs.get('email_receptor')
            guardar_acuse = kwargs.get('guardar_acuse', True)
            
            # Validar parámetros requeridos
            if not all([rfc_receptor, total, tipo_comprobante, motivo, certificado_base64, key_base64, password_key]):
                return ResultadoCancelacion.ResultadoError(
                    folio_fiscal,
                    "Parámetros incompletos",
                    "Faltan parámetros requeridos para la cancelación"
                )
            
            # Determinar URL según ambiente
            if pruebas:
                url = "https://pruebas.comercio-digital.mx/cancela4/cancelarUuid"
            else:
                url = "https://cancela.comercio-digital.mx/cancela4/cancelarUuid"
            
            logger.info(f"Cancelando UUID {folio_fiscal} en ambiente {'PRUEBAS' if pruebas else 'PRODUCCIÓN'}")
            
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
            
            # Preparar headers
            headers = {
                "Content-Type": "text/plain"
            }
            
            # Construir body según formato de Comercio Digital
            body_parts = [
                f"USER={usuario.replace('Ñ', '@')}",
                f"PWDW={password}",
                f"TIPO1=cfdi",
                f"UUID={folio_fiscal}",
                f"RFCR={rfc_receptor}",
                f"TOTAL={total}",
                f"TIPOC={tipo_comprobante}",
                f"MOTIVO={motivo}",
                f"PWDK={password_key}"
            ]
            
            # Agregar parámetros opcionales
            if rfc_emisor:
                body_parts.append(f"RFCE={rfc_emisor}")
            if email_emisor:
                body_parts.append(f"EMAILE={email_emisor}")
            if email_receptor:
                body_parts.append(f"EMAILR={email_receptor}")
            if motivo == "01" and uuid_relacionado:
                body_parts.append(f"UUIDREL={uuid_relacionado}")
            
            body_parts.append("ACUS=SI" if guardar_acuse else "ACUS=NO")
            body_parts.append(f"KEYF={key_base64}")
            body_parts.append(f"CERT={certificado_base64}")
            
            body = "\n".join(body_parts)
            
            # Realizar petición HTTP
            response = requests.post(
                url=url,
                headers=headers,
                data=body,
                timeout=30
            )
            
            logger.info(f"Respuesta del PAC - Status Code: {response.status_code}")
            
            # Procesar respuesta
            if response.status_code == 200:
                codigo = response.headers.get('codigo', '')
                
                if codigo == '000':
                    logger.info(f"Cancelación exitosa para UUID: {folio_fiscal}")
                    
                    acuse_data = {
                        "fecha": response.headers.get('fecha'),
                        "codigo": codigo,
                        "mensaje": response.headers.get('msg', 'Cancelación exitosa'),
                        "uuid": folio_fiscal,
                        "folios": [{
                            "uuid": folio_fiscal,
                            "estatus": "Cancelado"
                        }]
                    }
                    
                    if response.content:
                        acuse_data["acuse_xml"] = response.content.decode('utf-8', errors='ignore')
                    
                    return ResultadoCancelacion.ResultadoExito(folio_fiscal, acuse_data)
                else:
                    error_msg = response.headers.get('errmsg', 'Error desconocido del PAC')
                    logger.error(f"PAC rechazó cancelación. Código: {codigo}, Mensaje: {error_msg}")
                    
                    return ResultadoCancelacion.ResultadoError(
                        folio_fiscal,
                        f"Error del PAC (código {codigo})",
                        error_msg
                    )
            else:
                error_msg = f"Error HTTP {response.status_code}"
                detalle = response.text if response.text else "Sin detalles adicionales"
                
                logger.error(f"Error HTTP al cancelar UUID {folio_fiscal}: {error_msg}")
                
                return ResultadoCancelacion.ResultadoError(
                    folio_fiscal,
                    error_msg,
                    detalle
                )
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al cancelar UUID {folio_fiscal}")
            return ResultadoCancelacion.ResultadoError(
                folio_fiscal,
                "Timeout de conexión con el PAC",
                "La solicitud excedió el tiempo de espera"
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión al cancelar UUID {folio_fiscal}: {str(e)}")
            return ResultadoCancelacion.ResultadoError(
                folio_fiscal,
                "Error de conexión con el PAC",
                str(e)
            )
            
        except Exception as e:
            logger.exception(f"Error inesperado al cancelar UUID {folio_fiscal}")
            return ResultadoCancelacion.ResultadoError(
                folio_fiscal,
                "Error inesperado en la cancelación",
                str(e)
            )
