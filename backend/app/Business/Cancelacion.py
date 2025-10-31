"""
Cancelacion.py - Business Logic para operaciones de cancelación de CFDI
Maneja la cancelación de comprobantes usando el PAC Comercio Digital
"""

import logging
from typing import List
from datetime import datetime

from satcfdi.create.cancela.cancelacion import Cancelacion as SatCFDICancelacion, Folio as SatCFDIFolio
from satcfdi.pacs import Environment
from satcfdi.pacs.comerciodigital import ComercioDigital
from satcfdi.models import Signer

from .ResultadoCancelacion import ResultadoCancelacion

logger = logging.getLogger(__name__)


class CancelacionService:
    """
    Servicio para cancelar CFDI utilizando el PAC de Comercio Digital.
    """

    @classmethod
    def cancelar_cfdi(
        cls,
        folios: List[dict],
        cer_bytes: bytes,
        key_bytes: bytes,
        password: str,
        usuario_pac: str,
        contrasena_pac: str,
        pruebas: bool = True
    ) -> dict:
        try:
            # Validar que haya folios
            if not folios or not isinstance(folios, list):
                raise ValueError("Se requiere una lista de folios para cancelar")
            
            # Crear Signer con los certificados
            signer = Signer(cer_bytes, key_bytes, password)
            
            # Convertir folios de dict a objetos Folio de satcfdi
            folios_objetos = cls._convertir_folios(folios)
            logger.info(f"Se procesarán {len(folios_objetos)} folio(s) para cancelación")
            
            # Crear solicitud de cancelación
            cancelacion = SatCFDICancelacion(
                emisor=signer,
                folios=folios_objetos,
                fecha=datetime.utcnow()
            )
            
            # Procesar cancelación con el PAC
            return cls._procesar_cancelacion(
                cancelacion,
                usuario_pac,
                contrasena_pac,
                pruebas
            )
            
        except ValueError as e:
            logger.error(f"Error de validación: {str(e)}")
            return ResultadoCancelacion.ResultadoError(e)
        except Exception as e:
            logger.exception("Error inesperado al cancelar CFDI")
            return ResultadoCancelacion.ResultadoError(e)

    @classmethod
    def _convertir_folios(cls, folios: List[dict]) -> List[SatCFDIFolio]:
        """
        Convierte una lista de diccionarios a objetos Folio de satcfdi.
        """
        folios_objetos = []
        
        for i, folio_dict in enumerate(folios):
            if not isinstance(folio_dict, dict):
                raise ValueError(f"Folio en posición {i} debe ser un diccionario")
            
            uuid = folio_dict.get('uuid')
            motivo = folio_dict.get('motivo')
            folio_sustitucion = folio_dict.get('folioSustitucion')
            
            # Validar campos requeridos
            if not uuid:
                raise ValueError(f"Folio en posición {i} no tiene 'uuid'")
            if not motivo:
                raise ValueError(f"Folio en posición {i} no tiene 'motivo'")
            
            # Validar que el motivo sea válido (01, 02, 03, 04)
            if motivo not in ['01', '02', '03', '04']:
                raise ValueError(
                    f"Motivo '{motivo}' no válido. Debe ser: "
                    "01 (Comprobante emitido con errores con relación), "
                    "02 (Comprobante emitido con errores sin relación), "
                    "03 (No se llevó a cabo la operación), "
                    "04 (Operación nominativa relacionada en una factura global)"
                )
            
            # Si el motivo es 01, debe tener folioSustitucion
            if motivo == '01' and not folio_sustitucion:
                raise ValueError(
                    f"Folio en posición {i}: El motivo '01' requiere 'folioSustitucion'"
                )
            
            # Crear objeto Folio de satcfdi
            if folio_sustitucion:
                folio_obj = SatCFDIFolio(
                    uuid=uuid,
                    motivo=motivo,
                    folio_sustitucion=folio_sustitucion
                )
            else:
                folio_obj = SatCFDIFolio(
                    uuid=uuid,
                    motivo=motivo
                )
            
            folios_objetos.append(folio_obj)
            logger.debug(f"Folio convertido: UUID={uuid}, Motivo={motivo}")
        
        return folios_objetos

    @classmethod
    def _procesar_cancelacion(
        cls,
        cancelacion: SatCFDICancelacion,
        usuario_pac: str,
        contrasena_pac: str,
        pruebas: bool = True
    ) -> dict:
        """
        Procesa la cancelación con el PAC Comercio Digital.
        """
        try:
            # Configurar ambiente del PAC
            env = Environment.TEST if pruebas else Environment.PRODUCTION
            logger.info(f"Procesando cancelación en ambiente: {'PRUEBAS' if pruebas else 'PRODUCCIÓN'}")
            
            # Inicializar PAC
            pac = ComercioDigital(
                user=usuario_pac,
                password=contrasena_pac,
                environment=env
            )
            
            # Enviar solicitud de cancelación
            logger.info("Enviando solicitud de cancelación al PAC")
            acuse = pac.cancel_comprobante(cancelacion)
            
            # Retornar resultado exitoso
            return ResultadoCancelacion.ResultadoExito(acuse)
            
        except Exception as e:
            logger.exception('Error al cancelar CFDI con el PAC')
            return ResultadoCancelacion.ResultadoError(e)

    def cancelar(
        self,
        folios: List[dict],
        cer_bytes: bytes,
        key_bytes: bytes,
        password: str,
        usuario_pac: str,
        contrasena_pac: str,
        pruebas: bool = True
    ) -> dict:
        """
        Método de instancia para cancelar CFDI.
        Delega al método de clase.
        """
        return self.cancelar_cfdi(
            folios,
            cer_bytes,
            key_bytes,
            password,
            usuario_pac,
            contrasena_pac,
            pruebas
        )

cancelacion_service = CancelacionService()
