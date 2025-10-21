"""
Comprobante de Ingreso (Tipo "I")
Implementa validaciones y ajustes específicos para facturas de ingreso
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ComprobanteIngreso:
    """
    Clase para manejar la lógica de comprobantes tipo Ingreso (I).
    """
    
    def __init__(self, datos_json: Dict[str, Any]):
        self.datos = datos_json
        self.comprobante = datos_json.get("cfdi:Comprobante", {})
        self.errores: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []
    
    def validar(self) -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones específicas para tipo Ingreso
        """ 
        self._validar_tipo_comprobante()
        self._validar_total()
        self._validar_metodo_pago()
        self._validar_totales_calculados()
        self._validar_impuestos_requeridos()
        
        return {
            "valido": len(self.errores) == 0,
            "errores": self.errores,
            "warnings": self.warnings
        }
    
    def _validar_tipo_comprobante(self):
        """Verifica que el tipo sea 'I'"""
        tipo = self.comprobante.get("TipoDeComprobante")
        if tipo != "I":
            self.errores.append({
                "tipo": "error",
                "codigo": "ING001",
                "mensaje": f"TipoDeComprobante debe ser 'I' para Ingreso, se recibió '{tipo}'"
            })
    
    def _validar_total(self):
        """Valida que el Total sea mayor a 0"""
        try:
            total = float(self.comprobante.get("Total", 0))
            if total <= 0:
                self.errores.append({
                    "tipo": "error",
                    "codigo": "ING002",
                    "mensaje": f"Total debe ser mayor a 0 para comprobantes de Ingreso. Total actual: {total}"
                })
        except (ValueError, TypeError):
            self.errores.append({
                "tipo": "error",
                "codigo": "ING003",
                "mensaje": "Total no es un valor numérico válido"
            })
    
    def _validar_metodo_pago(self):
        """Valida que exista MetodoPago para tipo Ingreso"""
        metodo_pago = self.comprobante.get("MetodoPago")
        if not metodo_pago or metodo_pago == "":
            self.errores.append({
                "tipo": "error",
                "codigo": "ING004",
                "mensaje": "MetodoPago es requerido para comprobantes de Ingreso (PPD, PUE, etc.)"
            })
    
    def _validar_totales_calculados(self):
        """Valida que Total = SubTotal - Descuento + ImpuestosTrasladados - ImpuestosRetenidos"""
        try:
            subtotal = float(self.comprobante.get("SubTotal", 0))
            total = float(self.comprobante.get("Total", 0))
            descuento = float(self.comprobante.get("Descuento", 0) or 0)
            
            impuestos_data = self.comprobante.get("cfdi:Impuestos", {})
            total_tras = float(impuestos_data.get("TotalImpuestosTrasladados", 0) or 0)
            total_ret = float(impuestos_data.get("TotalImpuestosRetenidos", 0) or 0)
            
            calculado = round(subtotal - descuento + total_tras - total_ret, 2)
            
            if abs(calculado - total) > 0.01:
                self.warnings.append({
                    "tipo": "warning",
                    "codigo": "ING005",
                    "mensaje": f"Total ({total}) no coincide con SubTotal - Descuento + Trasladados - Retenidos ({calculado})"
                })
        except (ValueError, TypeError) as e:
            self.errores.append({
                "tipo": "error",
                "codigo": "ING006",
                "mensaje": f"Error al validar totales: {str(e)}"
            })
    
    def _validar_impuestos_requeridos(self):
        """Valida que los impuestos estén correctos según ObjetoImp"""
        conceptos_data = self.comprobante.get("cfdi:Conceptos", {})
        concepto_data = conceptos_data.get("cfdi:Concepto", {})
        
        if isinstance(concepto_data, dict):
            objeto_imp = concepto_data.get("ObjetoImp")
            impuestos = concepto_data.get("cfdi:Impuestos")
            
            # ObjetoImp = 02 significa que sí es objeto de impuestos
            if objeto_imp == "02" and not impuestos:
                self.warnings.append({
                    "tipo": "warning",
                    "codigo": "ING007",
                    "mensaje": "ObjetoImp='02' indica objeto de impuestos, pero no hay impuestos en concepto"
                })
    
    def ajustar_datos(self) -> Dict[str, Any]:
        """
        Aplica ajustes y normalizaciones específicas para tipo Ingreso
        """
        logger.info("Ajustando datos para comprobante tipo Ingreso")
        
        # Asegurar que TipoDeComprobante sea "I"
        if "cfdi:Comprobante" in self.datos:
            self.datos["cfdi:Comprobante"]["TipoDeComprobante"] = "I"
        
        # Recalcular totales si es necesario
        self._recalcular_totales()
        
        return self.datos
    
    def _recalcular_totales(self):
        """Recalcula Total basado en SubTotal, Descuento e Impuestos"""
        try:
            subtotal = float(self.comprobante.get("SubTotal", 0))
            descuento = float(self.comprobante.get("Descuento", 0) or 0)
            
            impuestos_data = self.comprobante.get("cfdi:Impuestos", {})
            total_tras = float(impuestos_data.get("TotalImpuestosTrasladados", 0) or 0)
            total_ret = float(impuestos_data.get("TotalImpuestosRetenidos", 0) or 0)
            
            total_calculado = round(subtotal - descuento + total_tras - total_ret, 2)
            
            # Actualizar Total si hay discrepancia
            total_actual = float(self.comprobante.get("Total", 0))
            if abs(total_calculado - total_actual) > 0.01:
                logger.warning(f"Ajustando Total de {total_actual} a {total_calculado}")
                self.datos["cfdi:Comprobante"]["Total"] = f"{total_calculado:.2f}"
        except (ValueError, TypeError) as e:
            logger.error(f"Error al recalcular totales: {str(e)}")
    
    def generar_xml(self) -> str:
        """
        Genera el XML del comprobante usando ConvertirJson
        """
        
        from ..ConvertirJson import ConvertirJson
        
        # Ajustar datos antes de generar
        datos_ajustados = self.ajustar_datos()
        
        if "datos_xml" in self.datos:
            # Se considera que se recibe datos como JSON, generar XML
            conversor = ConvertirJson(datos_ajustados)
            xml_resultado = conversor.GenerarXmlCFDI()
            return xml_resultado
        elif "xml" in self.datos:
            # Se considera que se recibe un XML directamente
            return self.datos["xml"]
        else:
            # Por defecto, asumir JSON y generar XML
            conversor = ConvertirJson(datos_ajustados)
            xml_resultado = conversor.GenerarXmlCFDI()
            return xml_resultado
        


__all__ = ["ComprobanteIngreso"]
