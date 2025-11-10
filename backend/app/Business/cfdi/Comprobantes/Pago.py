"""
Comprobante de Pago (Tipo "P")
Implementa validaciones y ajustes específicos para comprobantes de pago con complemento Pago 2.0
"""

import logging
from typing import Dict, Any, List
from decimal import Decimal

logger = logging.getLogger(__name__)


class ComprobantePago:
    """
    Clase para manejar la lógica de comprobantes tipo Pago (P).
    """
    
    def __init__(self, datos_json: Dict[str, Any]):
        # Normalizar la estructura de datos
        # Si viene con datosXML en el nivel superior, ajustar
        if "datosXML" in datos_json and "cfdi:Comprobante" not in datos_json:
            self.datos = datos_json  # Mantener estructura completa para búsqueda de complemento
            self.comprobante = datos_json.get("datosXML", {}).get("cfdi:Comprobante", {})
        else:
            self.datos = datos_json
            self.comprobante = datos_json.get("cfdi:Comprobante", {})
        
        self.errores: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []
    
    def validar(self) -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones específicas para tipo Pago
        """ 
        self._validar_tipo_comprobante()
        self._validar_valores_en_cero()
        self._validar_complemento_pago()
        self._validar_exportacion()
        
        return {
            "valido": len(self.errores) == 0,
            "errores": self.errores,
            "warnings": self.warnings
        }
    
    def _validar_tipo_comprobante(self):
        """Verifica que el tipo sea 'P'"""
        tipo = self.comprobante.get("TipoDeComprobante")
        if tipo != "P":
            self.errores.append({
                "tipo": "error",
                "codigo": "PAGO001",
                "mensaje": f"TipoDeComprobante debe ser 'P' para Pago, se recibió '{tipo}'"
            })
    
    def _validar_valores_en_cero(self):
        """
        Valida que SubTotal, Total y Descuento sean 0 para comprobantes de pago.
        Según el anexo 20, los comprobantes de pago deben tener estos valores en 0.
        """
        try:
            subtotal = float(self.comprobante.get("SubTotal", 0))
            total = float(self.comprobante.get("Total", 0))
            descuento = float(self.comprobante.get("Descuento", 0) or 0)
            
            if subtotal != 0:
                self.errores.append({
                    "tipo": "error",
                    "codigo": "PAGO002",
                    "mensaje": f"SubTotal debe ser 0 para comprobantes de Pago. Valor actual: {subtotal}"
                })
            
            if total != 0:
                self.errores.append({
                    "tipo": "error",
                    "codigo": "PAGO003",
                    "mensaje": f"Total debe ser 0 para comprobantes de Pago. Valor actual: {total}"
                })
            
            if descuento != 0:
                self.warnings.append({
                    "tipo": "warning",
                    "codigo": "PAGO004",
                    "mensaje": f"Descuento debe ser 0 para comprobantes de Pago. Valor actual: {descuento}"
                })
                
        except (ValueError, TypeError) as e:
            self.errores.append({
                "tipo": "error",
                "codigo": "PAGO005",
                "mensaje": f"Error al validar valores del comprobante: {str(e)}"
            })
    
    def _validar_complemento_pago(self):
        """
        Valida que exista el complemento de pago y tenga la estructura correcta
        """
        # Buscar el complemento de pago en diferentes ubicaciones posibles
        complemento_pago = None
        
        logger.info(f"DEBUG - Estructura completa de self.datos: {list(self.datos.keys())}")
        
        # Buscar en datosXML->complemento->pago20
        if self.datos.get('datosXML', {}).get('complemento', {}).get('pago20'):
            complemento_pago = self.datos['datosXML']['complemento']['pago20']
            logger.info("DEBUG - Complemento encontrado en datosXML->complemento->pago20")
        
        # Buscar directamente en complemento->pago20 (cuando ya se normalizó)
        elif self.datos.get('complemento', {}).get('pago20'):
            complemento_pago = self.datos['complemento']['pago20']
            logger.info("DEBUG - Complemento encontrado en complemento->pago20")
        
        # Buscar en cfdi:Comprobante->cfdi:Complemento
        elif self.datos.get('cfdi:Comprobante', {}).get('cfdi:Complemento', {}).get('pago20:Pagos'):
            complemento_pago = self.datos['cfdi:Comprobante']['cfdi:Complemento']['pago20:Pagos']
            logger.info("DEBUG - Complemento encontrado en cfdi:Comprobante->cfdi:Complemento->pago20:Pagos")
        
        # Buscar en datosXML->cfdi:Comprobante->cfdi:Complemento
        elif self.datos.get('datosXML', {}).get('cfdi:Comprobante', {}).get('cfdi:Complemento', {}).get('pago20:Pagos'):
            complemento_pago = self.datos['datosXML']['cfdi:Comprobante']['cfdi:Complemento']['pago20:Pagos']
            logger.info("DEBUG - Complemento encontrado en datosXML->cfdi:Comprobante->cfdi:Complemento->pago20:Pagos")
        
        # Buscar directamente en complemento_pago
        elif self.datos.get('complemento_pago'):
            complemento_pago = self.datos['complemento_pago']
            logger.info("DEBUG - Complemento encontrado en complemento_pago")
        
        if not complemento_pago:
            logger.error(f"DEBUG - No se encontró complemento de pago. Estructura de datos: {self.datos}")
            self.errores.append({
                "tipo": "error",
                "codigo": "PAGO006",
                "mensaje": "El complemento de pago (Pago 2.0) es obligatorio para comprobantes tipo 'P'"
            })
            return
        
        logger.info(f"DEBUG - Complemento encontrado: {list(complemento_pago.keys()) if isinstance(complemento_pago, dict) else type(complemento_pago)}")
        
        # Validar que exista al menos un pago
        pagos = complemento_pago.get('pago20:Pago') or complemento_pago.get('Pago') or complemento_pago.get('pagos')
        
        if not pagos:
            self.errores.append({
                "tipo": "error",
                "codigo": "PAGO007",
                "mensaje": "Debe existir al menos un elemento 'Pago' en el complemento de pago"
            })
            return
        
        # Convertir a lista si es un solo pago
        if isinstance(pagos, dict):
            pagos = [pagos]
        
        # Validar cada pago
        for idx, pago in enumerate(pagos, 1):
            self._validar_estructura_pago(pago, idx)
    
    def _validar_estructura_pago(self, pago: Dict[str, Any], indice: int):
        """Valida la estructura de un pago individual"""
        
        # Validar FechaPago (obligatorio)
        fecha_pago = pago.get('FechaPago') or pago.get('fecha_pago')
        if not fecha_pago:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO008_{indice}",
                "mensaje": f"FechaPago es obligatorio en Pago #{indice}"
            })
        
        # Validar FormaDePagoP (obligatorio)
        forma_pago = pago.get('FormaDePagoP') or pago.get('forma_de_pago_p')
        if not forma_pago:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO009_{indice}",
                "mensaje": f"FormaDePagoP es obligatorio en Pago #{indice}"
            })
        
        # Validar MonedaP (obligatorio)
        moneda = pago.get('MonedaP') or pago.get('moneda_p')
        if not moneda:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO010_{indice}",
                "mensaje": f"MonedaP es obligatorio en Pago #{indice}"
            })
        
        # Validar Monto (opcional, pero si existe debe ser > 0)
        monto = pago.get('Monto') or pago.get('monto')
        if monto:
            try:
                monto_decimal = Decimal(str(monto))
                if monto_decimal <= 0:
                    self.warnings.append({
                        "tipo": "warning",
                        "codigo": f"PAGO011_{indice}",
                        "mensaje": f"Monto en Pago #{indice} debe ser mayor a 0. Valor: {monto}"
                    })
            except:
                self.errores.append({
                    "tipo": "error",
                    "codigo": f"PAGO012_{indice}",
                    "mensaje": f"Monto en Pago #{indice} no es un valor numérico válido: {monto}"
                })
        
        # Validar DoctoRelacionado (al menos uno es obligatorio)
        doctos = pago.get('pago20:DoctoRelacionado') or pago.get('DoctoRelacionado') or pago.get('docto_relacionado')
        
        if not doctos:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO013_{indice}",
                "mensaje": f"Debe existir al menos un DoctoRelacionado en Pago #{indice}"
            })
            return
        
        # Convertir a lista si es un solo documento
        if isinstance(doctos, dict):
            doctos = [doctos]
        
        # Validar cada documento relacionado
        for doc_idx, docto in enumerate(doctos, 1):
            self._validar_documento_relacionado(docto, indice, doc_idx)
    
    def _validar_documento_relacionado(self, docto: Dict[str, Any], indice_pago: int, indice_doc: int):
        """Valida la estructura de un documento relacionado"""
        
        # Validar IdDocumento (UUID del documento relacionado - obligatorio)
        id_documento = docto.get('IdDocumento') or docto.get('id_documento')
        if not id_documento:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO014_{indice_pago}_{indice_doc}",
                "mensaje": f"IdDocumento es obligatorio en DoctoRelacionado #{indice_doc} del Pago #{indice_pago}"
            })
        
        # Validar ImpPagado (obligatorio)
        imp_pagado = docto.get('ImpPagado') or docto.get('imp_pagado')
        if imp_pagado is None:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO015_{indice_pago}_{indice_doc}",
                "mensaje": f"ImpPagado es obligatorio en DoctoRelacionado #{indice_doc} del Pago #{indice_pago}"
            })
        
        # Validar ImpSaldoAnt (obligatorio)
        imp_saldo_ant = docto.get('ImpSaldoAnt') or docto.get('imp_saldo_ant')
        if imp_saldo_ant is None:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO016_{indice_pago}_{indice_doc}",
                "mensaje": f"ImpSaldoAnt es obligatorio en DoctoRelacionado #{indice_doc} del Pago #{indice_pago}"
            })
        
        # Validar ObjetoImpDR (obligatorio en CFDI 4.0)
        objeto_imp = docto.get('ObjetoImpDR') or docto.get('objeto_imp_dr')
        if not objeto_imp:
            self.errores.append({
                "tipo": "error",
                "codigo": f"PAGO017_{indice_pago}_{indice_doc}",
                "mensaje": f"ObjetoImpDR es obligatorio en DoctoRelacionado #{indice_doc} del Pago #{indice_pago}"
            })
       
        # Si ObjetoImpDR es "02", ImpuestosDR es obligatorio
        if objeto_imp == "02":
            impuestos_dr = docto.get('ImpuestosDR') or docto.get('impuestos_dr')
            if not impuestos_dr:
                self.errores.append({
                    "tipo": "error",
                    "codigo": f"PAGO018_{indice_pago}_{indice_doc}",
                    "mensaje": f"ImpuestosDR es obligatorio en DoctoRelacionado #{indice_doc} del Pago #{indice_pago} cuando ObjetoImpDR es '02'"
                })
    
    def _validar_exportacion(self):
        """
        Valida el campo Exportacion que es obligatorio en CFDI 4.0
        Para pagos generalmente es "01" (No aplica)
        """
        exportacion = self.comprobante.get("Exportacion")
        if not exportacion:
            self.warnings.append({
                "tipo": "warning",
                "codigo": "PAGO018",
                "mensaje": "El campo Exportacion es obligatorio en CFDI 4.0. Se recomienda usar '01' para pagos."
            })
    
    def ajustar_datos(self) -> Dict[str, Any]:
        """
        Aplica ajustes y normalizaciones específicas para tipo Pago
        """
        logger.info("Ajustando datos para comprobante tipo Pago")
        
        # Asegurar estructura correcta
        if "cfdi:Comprobante" not in self.datos:
            if "datosXML" in self.datos and "cfdi:Comprobante" in self.datos["datosXML"]:
                self.datos = self.datos["datosXML"]
            else:
                # Crear estructura base
                self.datos = {"cfdi:Comprobante": self.comprobante}
        
        comprobante_data = self.datos.get("cfdi:Comprobante", {})
        
        # Forzar TipoDeComprobante a "P"
        comprobante_data["TipoDeComprobante"] = "P"
        
        # Forzar valores en 0
        comprobante_data["SubTotal"] = "0"
        comprobante_data["Total"] = "0"
        comprobante_data["Moneda"] = "XXX"  # Moneda XXX para comprobantes de pago
        
        # Si no existe Exportacion, agregar valor por defecto
        if "Exportacion" not in comprobante_data:
            comprobante_data["Exportacion"] = "01"
        
        self.datos["cfdi:Comprobante"] = comprobante_data
        
        return self.datos
    
    def generar_xml(self) -> str:
        """
        Genera el XML del comprobante de pago usando satcfdi
        """
        from ..ConvertirJson import ConvertirJson
        
        # Ajustar datos antes de generar
        datos_ajustados = self.ajustar_datos()
        
        # Generar XML usando ConvertirJson con soporte para Pago 2.0
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


__all__ = ["ComprobantePago"]
