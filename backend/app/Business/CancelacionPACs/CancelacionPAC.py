"""
Clase abstracta para definir la interfaz común de cancelación de CFDIs.

Esta clase define el contrato que deben cumplir todas las implementaciones
de cancelación para diferentes proveedores PAC.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class CancelacionPAC(ABC):
    """
    Clase base abstracta para cancelación de CFDIs con diferentes PACs.
    
    Define la interfaz común que deben implementar todas las clases
    concretas de cancelación para garantizar consistencia en el sistema.
    """
    
    @abstractmethod
    def cancelar(
        self, 
        folio_fiscal: str, 
        usuario: str, 
        password: str, 
        pruebas: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Cancela un CFDI dado su folio fiscal (UUID).
        
        Args:
            folio_fiscal (str): UUID del comprobante a cancelar.
            usuario (str): Usuario del PAC.
            password (str): Contraseña del PAC.
            pruebas (bool): Indica si es ambiente de pruebas. Por defecto True.
            **kwargs: Parámetros adicionales específicos del PAC (RFC emisor, 
                     motivo cancelación, UUID sustitución, etc.)
        
        Returns:
            Dict[str, Any]: Diccionario con el resultado de la cancelación:
                - success (bool): True si la cancelación fue exitosa
                - message (str): Mensaje descriptivo del resultado
                - data (Optional[dict]): Datos adicionales de la respuesta
                - error (Optional[str]): Mensaje de error si aplica
        
        Raises:
            NotImplementedError: Si el método no está implementado en la subclase.
            ValueError: Si los parámetros son inválidos.
            Exception: Para errores específicos del PAC.
        """
        raise NotImplementedError(
            f"El método 'cancelar' debe ser implementado en la clase {self.__class__.__name__}"
        )
    
    @abstractmethod
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
            folio_fiscal (str): UUID a validar.
            usuario (str): Usuario del PAC.
            password (str): Contraseña del PAC.
            **kwargs: Parámetros adicionales específicos del PAC.
        
        Returns:
            tuple[bool, Optional[str]]: Tupla con (es_válido, mensaje_error).
                - Si es válido: (True, None)
                - Si no es válido: (False, "mensaje descriptivo del error")
        """
        raise NotImplementedError(
            f"El método 'validar_parametros' debe ser implementado en la clase {self.__class__.__name__}"
        )
    
    def obtener_tipo_pac(self) -> str:
        """
        Retorna el identificador del tipo de PAC.
        
        Returns:
            str: Identificador del PAC (ej: 'comerciodigital', 'finkok', etc.)
        
        Note:
            Este método debe ser sobrescrito en las clases concretas.
        """
        return "desconocido"
    
    def formatear_respuesta(
        self, 
        success: bool, 
        message: str, 
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Formatea la respuesta de cancelación en un formato estándar.
        
        Args:
            success (bool): Indica si la operación fue exitosa.
            message (str): Mensaje descriptivo del resultado.
            data (Optional[Dict[str, Any]]): Datos adicionales de la respuesta.
            error (Optional[str]): Mensaje de error si aplica.
        
        Returns:
            Dict[str, Any]: Respuesta formateada con estructura consistente.
        """
        respuesta = {
            "success": success,
            "message": message,
            "tipo_pac": self.obtener_tipo_pac()
        }
        
        if data is not None:
            respuesta["data"] = data
        
        if error is not None:
            respuesta["error"] = error
        
        return respuesta


class CancelacionPACException(Exception):
    """
    Excepción base para errores de cancelación con PACs.
    
    Esta clase permite manejar errores específicos de cancelación
    de manera consistente en todo el sistema.
    """
    
    def __init__(self, message: str, tipo_pac: Optional[str] = None, detalles: Optional[Dict] = None):
        """
        Inicializa la excepción de cancelación.
        
        Args:
            message (str): Mensaje descriptivo del error.
            tipo_pac (Optional[str]): Tipo de PAC donde ocurrió el error.
            detalles (Optional[Dict]): Detalles adicionales del error.
        """
        self.message = message
        self.tipo_pac = tipo_pac
        self.detalles = detalles or {}
        super().__init__(self.message)
    
    def __str__(self):
        """Representación en string de la excepción."""
        base = f"Error de cancelación: {self.message}"
        if self.tipo_pac:
            base += f" [PAC: {self.tipo_pac}]"
        return base
