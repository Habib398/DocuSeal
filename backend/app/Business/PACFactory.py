"""
Factory para crear instancias de diferentes PACs.

Este módulo proporciona un patrón Factory para la creación
de instancias de diferentes proveedores PAC (Proveedores 
Autorizados de Certificación) de manera centralizada y extensible.

PACs Soportados:
- comerciodigital (actual)
- finkok
- diverza
- mysuite
- prodigia
- swsapien
- sat
"""


class PACFactory:
    """
    Factory para crear instancias de diferentes PACs.
    
    Proporciona un punto centralizado para la instanciación de PACs
    y facilita la adición de nuevos proveedores en el futuro.
    """
    
    # Mapeo de tipos de PAC a sus clases correspondientes
    # Se implementarán las importaciones en versiones futuras
    PAC_CLASSES = {
        # 'comerciodigital': ComercioDigital,
        # 'finkok': Finkok,
        # 'diverza': Diverza,
        # 'mysuite': MySuite,
        # 'prodigia': Prodigia,
        # 'swsapien': SWSapien,
        # 'sat': SAT,
    }
    
    @classmethod
    def crear_pac(cls, tipo_pac: str, usuario: str, password: str, pruebas: bool = True):
        """
        Crea una instancia del PAC especificado.
        
        Args:
            tipo_pac (str): Tipo de PAC (comerciodigital, finkok, etc.)
            usuario (str): Usuario del PAC
            password (str): Contraseña del PAC
            pruebas (bool): Si es ambiente de pruebas. Por defecto True.
            
        Returns:
            Instancia del PAC correspondiente
            
        Raises:
            ValueError: Si el tipo de PAC no está soportado
            NotImplementedError: Si el PAC aún no está implementado
            
        Note:
            Esta función está lista para ser implementada en versiones futuras.
            Actualmente es un stub que lanza NotImplementedError.
        """
        raise NotImplementedError(
            "La funcionalidad de PACFactory aún no ha sido implementada. "
            "Por favor, espere futuras versiones para el soporte multi-PAC."
        )
    
    @classmethod
    def tipos_disponibles(cls) -> list:
        """
        Retorna lista de tipos de PAC soportados.
        
        Returns:
            list: Lista con los identificadores de PACs disponibles.
            
        Note:
            Los tipos de PAC se cargarán cuando la implementación esté completa.
        """
        return list(cls.PAC_CLASSES.keys())
    
    @classmethod
    def es_pac_valido(cls, tipo_pac: str) -> bool:
        """
        Verifica si el tipo de PAC especificado es válido.
        
        Args:
            tipo_pac (str): Tipo de PAC a validar.
            
        Returns:
            bool: True si el PAC es válido, False en caso contrario.
        """
        return tipo_pac.lower() in cls.PAC_CLASSES
    
    @classmethod
    def obtener_pac_default(cls) -> str:
        """
        Retorna el tipo de PAC por defecto.
        
        Returns:
            str: Identificador del PAC por defecto ('comerciodigital').
        """
        return 'comerciodigital'


# Funciones de utilidad para futuras implementaciones

def validar_tipo_pac(tipo_pac: str) -> bool:
    """
    Función utilitaria para validar un tipo de PAC.
    
    Args:
        tipo_pac (str): Tipo de PAC a validar.
        
    Returns:
        bool: True si es válido, False en caso contrario.
    """
    return PACFactory.es_pac_valido(tipo_pac)


def obtener_tipos_pac_disponibles() -> list:
    """
    Función utilitaria para obtener tipos de PAC disponibles.
    
    Returns:
        list: Lista de tipos de PAC soportados.
    """
    return PACFactory.tipos_disponibles()
