"""
ResultadoCancelacion.py - Clase para estandarizar respuestas de operaciones de cancelación
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ResultadoCancelacion:
    """
    Clase para estandarizar las respuestas de operaciones de cancelación de CFDI.
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
    def ResultadoExito(uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una respuesta estandarizada para cancelación exitosa.
        """
        
        return {
            "codigo": 0,
            "mensaje": "Cancelación exitosa",
            "uuid": uuid,
            "data": data
        }
    
    @classmethod
    def ResultadoError(cls, uuid: str, error: str, detalle: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea una respuesta estandarizada para error en cancelación.
        """
        
        # Intentar buscar código de error en la matriz
        codigo_cfdi = None
        descripcion_error = error
        
        try:
            matriz = cls._cargar_matriz_errores()
            
            # Buscar códigos en el mensaje de error
            for codigo in matriz.keys():
                if codigo in error or (detalle and codigo in detalle):
                    codigo_cfdi = codigo
                    descripcion_error = matriz[codigo]
                    break
            
            # Si no se encontró código específico, usar genérico
            if not codigo_cfdi:
                codigo_cfdi = "CAN000"  # Código genérico para cancelación
                
        except Exception as e:
            logger.exception("Error al procesar código de error en matriz")
            codigo_cfdi = "CAN000"
        
        result = {
            "codigo": -1,
            "mensaje": descripcion_error,
            "uuid": uuid,
            "error": error
        }
        
        if detalle:
            result["detalle"] = detalle
            
        return result
    
    @classmethod
    def ResultadoMultiple(cls, resultados: list) -> Dict[str, Any]:
        """
        Crea una respuesta estandarizada para múltiples cancelaciones.
        """
        if not resultados:
            return {
                "codigo": -1,
                "mensaje": "No se procesaron cancelaciones",
                "total": 0,
                "exitosos": 0,
                "errores": 0,
                "resultados": []
            }
        
        exitosos = [r for r in resultados if r.get("codigo") == 0]
        errores = [r for r in resultados if r.get("codigo") != 0]
        
        return {
            "codigo": 0 if errores == [] else -1,
            "mensaje": f"Procesadas {len(resultados)} cancelaciones",
            "total": len(resultados),
            "exitosos": len(exitosos),
            "errores": len(errores),
            "resultados": resultados
        }