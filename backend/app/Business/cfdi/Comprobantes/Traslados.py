"""
Comprobante de Traslado (Tipo "T")
Implementa validaciones y ajustes específicos para comprobantes de traslado
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ComprobanteTraslado:
    """
    Clase para manejar la lógica de comprobantes tipo Traslado (T).
    """
    
    def __init__(self, datos_json: Dict[str, Any]):
        self.datos = datos_json
        self.comprobante = datos_json.get("cfdi:Comprobante", {})
        self.errores: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []
    
    def validar(self) -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones específicas para tipo Traslado
        """
        logger.info("Validando comprobante tipo Traslado (T)")
        
        self._validar_tipo_comprobante()
        self._validar_total_cero()
        self._validar_metodo_pago()
        self._validar_impuestos_comprobante()
        self._validar_subtotal()
        
        return {
            "valido": len(self.errores) == 0,
            "errores": self.errores,
            "warnings": self.warnings
        }
    
    def _validar_tipo_comprobante(self):
        """Verifica que el tipo sea 'T'"""
        tipo = self.comprobante.get("TipoDeComprobante")
        if tipo != "T":
            self.errores.append({
                "tipo": "error",
                "codigo": "TRA001",
                "mensaje": f"TipoDeComprobante debe ser 'T' para Traslado, se recibió '{tipo}'"
            })
    
    def _validar_total_cero(self):
        """
        Valida que el Total sea exactamente 0
        """
        try:
            total = float(self.comprobante.get("Total", 0))
            if abs(total) > 0.001:  # Permitir tolerancia mínima por redondeo
                self.errores.append({
                    "tipo": "error",
                    "codigo": "TRA002",
                    "mensaje": f"Total debe ser 0.00 para comprobantes de Traslado. Total actual: {total} (Regla CFDI40109)"
                })
        except (ValueError, TypeError):
            self.errores.append({
                "tipo": "error",
                "codigo": "TRA003",
                "mensaje": "Total no es un valor numérico válido"
            })
    
    def _validar_metodo_pago(self):
        """
        Valida que NO exista MetodoPago
        """
        metodo_pago = self.comprobante.get("MetodoPago")
        if metodo_pago and metodo_pago != "":
            self.errores.append({
                "tipo": "error",
                "codigo": "TRA004",
                "mensaje": f"MetodoPago debe omitirse para comprobantes de Traslado. Se encontró: '{metodo_pago}' (Regla CFDI40125)"
            })
    
    def _validar_impuestos_comprobante(self):
        """
        Valida que NO exista elemento cfdi:Impuestos a nivel comprobante
        """
        impuestos_data = self.comprobante.get("cfdi:Impuestos")
        if impuestos_data and len(impuestos_data) > 0:
            # Verificar si hay contenido real (no solo diccionario vacío)
            tiene_contenido = False
            if isinstance(impuestos_data, dict):
                # Buscar cualquier clave que tenga valor
                for key, value in impuestos_data.items():
                    if value and value != "" and value != {}:
                        tiene_contenido = True
                        break
            
            if tiene_contenido:
                self.errores.append({
                    "tipo": "error",
                    "codigo": "TRA005",
                    "mensaje": "El elemento cfdi:Impuestos no debe existir a nivel comprobante para tipo Traslado (Regla CFDI40201)"
                })
    
    def _validar_subtotal(self):
        """Valida que SubTotal sea mayor a 0"""
        try:
            subtotal = float(self.comprobante.get("SubTotal", 0))
            if subtotal <= 0:
                self.warnings.append({
                    "tipo": "warning",
                    "codigo": "TRA006",
                    "mensaje": f"SubTotal debe ser mayor a 0 para comprobantes de Traslado. SubTotal actual: {subtotal}"
                })
        except (ValueError, TypeError):
            self.errores.append({
                "tipo": "error",
                "codigo": "TRA007",
                "mensaje": "SubTotal no es un valor numérico válido"
            })

    def _validar_uso_cfdi(self):
        """Valida que UsoCFDI sea 'S01'"""
        uso_cfdi = self.comprobante.get("UsoCFDI")
        if uso_cfdi != "S01":
            self.warnings.append({
                "tipo": "warning",
                "codigo": "TRA008",
                "mensaje": f"UsoCFDI recomendado para Traslado es 'S01'. Se recibió '{uso_cfdi}'"
            })
    
    def ajustar_datos(self) -> Dict[str, Any]:
        """
        Aplica ajustes y normalizaciones específicas para tipo Traslado
        """
        
        if "cfdi:Comprobante" not in self.datos:
            return self.datos
        
        # Asegurar que TipoDeComprobante sea "T"
        self.datos["cfdi:Comprobante"]["TipoDeComprobante"] = "T"
        
        # Forzar Total = 0.00
        self.datos["cfdi:Comprobante"]["Total"] = "0.00"

        # Validar UsoCFDI 
        self.datos["cfdi:Comprobante"].setdefault("UsoCFDI", "S01")
        self.datos["cfdi:Comprobante"]["UsoCFDI"] = "S01"
        
        # Eliminar MetodoPago si existe
        if "MetodoPago" in self.datos["cfdi:Comprobante"]:
            del self.datos["cfdi:Comprobante"]["MetodoPago"]
        
        # Eliminar cfdi:Impuestos a nivel comprobante si existe
        if "cfdi:Impuestos" in self.datos["cfdi:Comprobante"]:
            del self.datos["cfdi:Comprobante"]["cfdi:Impuestos"]
        
        return self.datos
    
    def generar_xml(self) -> str:
        """
        Genera el XML del comprobante usando ConvertirJson
        con ajustes específicos para Traslado
        """
        
        from ..ConvertirJson import ConvertirJson
        
        # Ajustar datos antes de generar
        datos_ajustados = self.ajustar_datos()

        # Siempre generar XML desde JSON cuando viene de ComprobanteFactory
        conversor = ConvertirJson()
        cfdi_objeto = conversor.convertir_a_cfdi({"datosXML": datos_ajustados})
        xml_element = cfdi_objeto.to_xml()
        
        # Agregar NoCertificado al XML si está presente en los datos originales
        no_certificado = self.comprobante.get('NoCertificado')
        if no_certificado:
            xml_element.set('NoCertificado', str(no_certificado))
        
        from lxml import etree
        xml_resultado = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
        return xml_resultado


__all__ = ["ComprobanteTraslado"]
