"""
Configuración de Mensajes
Este módulo contiene los mensajes por defecto utilizados para notificaciones
de correo.
"""


class ConfiguracionMensajes:
    """
    Clase que gestiona los mensajes del sistema.
    Proporciona métodos para generar mensajes personalizados con datos de CFDI.
    """
    
    # Mapeo de tipos de comprobante a sus nombres descriptivos
    TIPOS_COMPROBANTE = {
        'T': 'Traslado',
        'I': 'Ingreso',
        'P': 'Pago'
    }
    
    # Firma estándar para los correos
    FIRMA_CORREO_TIMBRADO = "\n\nAtentamente,\nEquipo DocuSeal"
    
    @staticmethod
    def traducir_tipo_comprobante(tipo_comprobante: str) -> str:
        """
        Traduce la letra del tipo de comprobante a su nombre descriptivo.
        """
        return ConfiguracionMensajes.TIPOS_COMPROBANTE.get(tipo_comprobante, tipo_comprobante)
    
    @staticmethod
    def obtener_asunto_timbrado(tipo_comprobante: str = None) -> str:
        """
        Genera el asunto para correos de CFDI timbrado.
            tipo_comprobante: Tipo de comprobante (ej: 'I', 'T', 'P')
        """
        if tipo_comprobante:
            nombre_comprobante = ConfiguracionMensajes.traducir_tipo_comprobante(tipo_comprobante)
            return f"Envío de comprobante tipo: {nombre_comprobante}"
        return "Envío de comprobante timbrado"
    
    @staticmethod
    def obtener_cuerpo_timbrado(
        tipo_comprobante: str = None,
        folio: str = None,
        uuid: str = None
    ) -> str:
        """
        Genera el cuerpo para correos de CFDI timbrado.
            tipo_comprobante: Tipo de comprobante (ej: 'I', 'T', 'P')
            folio: Folio del comprobante
            uuid: UUID del timbrado
        """
        cuerpo = "Se adjunta su comprobante fiscal digital timbrado."
        
        if tipo_comprobante:
            nombre_comprobante = ConfiguracionMensajes.traducir_tipo_comprobante(tipo_comprobante)
            cuerpo += f"\n\nTipo de comprobante: {nombre_comprobante}"
        
        if folio:
            cuerpo += f"\nFolio: {folio}"
        
        if uuid:
            cuerpo += f"\nUUID del timbrado: {uuid}"
        
        # Agregar firma
        cuerpo += ConfiguracionMensajes.FIRMA_CORREO_TIMBRADO
        
        return cuerpo
    
    @staticmethod
    def obtener_firma() -> str:
        """
        Retorna la firma estándar para los correos.
        
        Returns:
            Firma del correo
        """
        return ConfiguracionMensajes.FIRMA_CORREO_TIMBRADO
