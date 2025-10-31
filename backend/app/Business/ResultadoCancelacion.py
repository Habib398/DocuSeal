"""
ResultadoCancelacion.py - Formatea las respuestas de cancelación de CFDI
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ResultadoCancelacion:
    """
    Clase para formatear los resultados de cancelación de CFDI.
    """
    
    _matriz_errores: Optional[Dict[str, str]] = None
    
    @classmethod
    def _cargar_matriz_errores(cls) -> Dict[str, str]:
        """Carga la matriz de errores desde el archivo matriz_errores.txt"""
        if cls._matriz_errores is not None:
            return cls._matriz_errores
        
        matriz = {}
        try:
            # Obtener la ruta del archivo de matriz de errores
            current_dir = os.path.dirname(os.path.abspath(__file__))
            matriz_path = os.path.join(current_dir, '..', 'Data', 'matriz_errores.txt')
            
            if os.path.exists(matriz_path):
                with open(matriz_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '|' in line:
                            parts = line.split('|', 1)
                            if len(parts) == 2:
                                codigo, mensaje = parts
                                matriz[codigo.strip()] = mensaje.strip()
                logger.info(f"Matriz de errores cargada: {len(matriz)} códigos")
            else:
                logger.warning(f"No se encontró el archivo de matriz de errores en: {matriz_path}")
        except Exception as e:
            logger.exception(f"Error al cargar matriz de errores: {e}")
        
        cls._matriz_errores = matriz
        return matriz
    
    @staticmethod
    def ResultadoExito(acuse: Any) -> Dict[str, Any]:
        """
        Formatea un resultado exitoso de cancelación.
        """
        try:
            # Obtener el acuse XML
            acuse_xml = None
            if hasattr(acuse, 'xml'):
                xml = acuse.xml
                if isinstance(xml, (bytes, bytearray)):
                    try:
                        acuse_xml = xml.decode('utf-8')
                    except Exception:
                        acuse_xml = xml.decode('utf-8', errors='replace')
                else:
                    acuse_xml = xml
            
            # Obtener fecha del acuse si está disponible
            fecha_cancelacion = None
            if hasattr(acuse, 'date'):
                fecha_cancelacion = str(acuse.date)
            
            # Obtener información de los folios
            folios_info = []
            if hasattr(acuse, 'uuids'):
                folios_info = [{"uuid": uuid} for uuid in acuse.uuids]
            
            return {
                "codigo": 0,
                "mensaje": "Cancelación exitosa",
                "acuse": acuse_xml,
                "fecha_cancelacion": fecha_cancelacion,
                "folios": folios_info
            }
            
        except Exception as e:
            logger.exception('Error al formatear resultado de cancelación exitosa')
            return {
                "codigo": 0,
                "mensaje": "Cancelación exitosa (error al formatear detalles)",
                "acuse": None
            }

    @classmethod
    def ResultadoError(cls, exc: Exception) -> Dict[str, Any]:
        """
        Formatea un resultado de error de cancelación.
        """
        msg = str(exc)
        codigo_cfdi = None
        descripcion_error = None
        cuerpo = None

        try:
            r = getattr(exc, 'response', None)
            if r is not None:
                # Extraer información de headers y body de la respuesta HTTP
                headers = getattr(r, 'headers', {}) or {}
                msg = headers.get('errmsg', msg)
                cuerpo = getattr(r, 'text', None)
        except Exception:
            logger.exception('Error al extraer información de la excepción del PAC')

        # Buscar el código CFDI en la matriz de errores
        matriz = cls._cargar_matriz_errores()
        
        # Buscar códigos CFDI en el mensaje o cuerpo
        for codigo in matriz.keys():
            if codigo in msg or codigo in str(cuerpo or ''):
                codigo_cfdi = codigo
                descripcion_error = matriz[codigo]
                break
        
        # Si no se encontró código en la matriz, usar mensaje genérico
        if not codigo_cfdi:
            descripcion_error = msg
            codigo_cfdi = "CANC000"

        result = {
            "errores": [{
                "tipo": "error",
                "codigo": codigo_cfdi,
                "mensaje": descripcion_error
            }]
        }

        return result
