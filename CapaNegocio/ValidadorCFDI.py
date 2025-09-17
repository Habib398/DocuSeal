from typing import List, Dict, Any

# Clase generada por Copilot

class ValidadorCFDI:
    """Valida reglas básicas antes de timbrar (no sustituye validación XSD ni PAC)."""

    def __init__(self, datos_xml: Dict[str, Any]):
        self.datos = datos_xml or {}
        self.comprobante = self.datos.get("cfdi:Comprobante", {})
        self.resultado: List[Dict[str, str]] = []

    def agregar(self, tipo: str, codigo: str, mensaje: str):
        self.resultado.append({"tipo": tipo, "codigo": codigo, "mensaje": mensaje})

    def validar_totales(self):
        try:
            subtotal = float(self.comprobante.get("SubTotal", 0))
        except Exception:
            self.agregar("error", "LOC001", "SubTotal no numérico")
            subtotal = 0
        try:
            total = float(self.comprobante.get("Total", 0))
        except Exception:
            self.agregar("error", "LOC002", "Total no numérico")
            total = 0
        descuento = 0.0
        if self.comprobante.get("Descuento") not in (None, ""):
            try:
                descuento = float(self.comprobante.get("Descuento"))
            except Exception:
                self.agregar("error", "LOC003", "Descuento no numérico")
        impuestos_data = self.comprobante.get("cfdi:Impuestos", {})
        try:
            total_tras = float(impuestos_data.get("TotalImpuestosTrasladados", 0) or 0)
        except Exception:
            total_tras = 0
            self.agregar("warning", "LOC004", "TotalImpuestosTrasladados no numérico")
        try:
            total_ret = float(impuestos_data.get("TotalImpuestosRetenidos", 0) or 0)
        except Exception:
            total_ret = 0
            self.agregar("warning", "LOC005", "TotalImpuestosRetenidos no numérico")

        calculado = round(subtotal - descuento + total_tras - total_ret, 2)
        if total and abs(calculado - total) > 0.01:
            self.agregar(
                "warning",
                "LOC006",
                f"Total ({total}) no coincide con SubTotal - Descuento + Trasladados - Retenidos ({calculado})."
            )

    def validar_emisor_receptor(self):
        emisor = self.comprobante.get("cfdi:Emisor", {})
        receptor = self.comprobante.get("cfdi:Receptor", {})
        if not emisor.get("Rfc"):
            self.agregar("error", "LOC010", "Falta Rfc en Emisor")
        if not receptor.get("Rfc"):
            self.agregar("error", "LOC011", "Falta Rfc en Receptor")
        if emisor.get("Rfc") and receptor.get("Rfc") and emisor.get("Rfc") == receptor.get("Rfc"):
            self.agregar("warning", "LOC012", "Rfc Emisor y Receptor iguales (verificar si procede)")

    def ejecutar(self) -> List[Dict[str, str]]:
        self.validar_totales()
        self.validar_emisor_receptor()
        return self.resultado

__all__ = ["ValidadorCFDI"]
