import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ResultadoTimbrado:
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
    def ResultadoExito(doc: Any) -> Dict[str, Any]:
        # Obtener cuerpo XML y decodificar si viene en bytes
        cuerpo = None
        try:
            xml = getattr(doc, 'xml', None)
            if isinstance(xml, (bytes, bytearray)):
                try:
                    cuerpo = xml.decode('utf-8')
                except Exception:
                    # fallback: decode con reemplazo de errores
                    cuerpo = xml.decode('utf-8', errors='replace')
            else:
                cuerpo = xml
        except Exception as e:
            logger.exception('Error al procesar xml del documento')
            cuerpo = None

        uuid = getattr(doc, 'document_id', None)

        return {
            "codigo": 0,
            "mensaje": "Timbrado exitoso",
            "uuid": uuid,
            "cuerpo": cuerpo,
        }

    @classmethod
    def ResultadoError(cls, exc: Exception) -> Dict[str, Any]:
        msg = str(exc)
        codigo_cfdi = None
        descripcion_error = None

        try:
            r = getattr(exc, 'response', None)
            if r is not None:
                # Algunas librerías ponen detalles en headers y text
                headers = getattr(r, 'headers', {}) or {}
                msg = headers.get('errmsg', msg)
                cuerpo = getattr(r, 'text', None)
        except Exception:
            logger.exception('Error al extraer información de la excepción del PAC')
            cuerpo = None

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

        result = {
            "codigo_cfdi": codigo_cfdi,
            "descripcion": descripcion_error,
        }

        return result
