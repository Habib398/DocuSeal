from jinja2 import Template, Environment, FileSystemLoader
import json
import os
from lxml import etree

class InyectorPDF:
    def __init__(self, template_path: str = None):
        if template_path is None:
            # Usar la ruta del archivo actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.template_dir = current_dir
            self.template_name = "PDF.html"
            self.css_path = os.path.join(os.path.dirname(current_dir), "css", "PDF.css")
        else:
            self.template_dir = os.path.dirname(template_path)
            self.template_name = os.path.basename(template_path)
            self.css_path = None
        
        # Configurar Jinja2
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        self.template = self.env.get_template(self.template_name)
    
    def leer_css(self) -> str:
        
        if self.css_path and os.path.exists(self.css_path):
            with open(self.css_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def extraer_datos_json(self, datos_json: dict, xml_sellado: str = None, cadena_original: str = None) -> dict:
        # Obtener el nodo principal del CFDI
        # Puede venir como "datosXML" (estructura JSON) o "xml" (string o dict)
        comprobante_data = datos_json.get("datosXML") or datos_json.get("xml", {})
        
        # Si es un dict, buscar el nodo Comprobante
        if isinstance(comprobante_data, dict):
            comprobante = comprobante_data.get("cfdi:Comprobante", comprobante_data)
        else:
            comprobante = {}
        
        # Extraer datos del Emisor
        emisor_data = comprobante.get("cfdi:Emisor", {})
        emisor = {
            "rfc": emisor_data.get("Rfc", ""),
            "nombre": emisor_data.get("Nombre", ""),
            "regimen_fiscal": ""  # Se obtendrá de la BD de catálogos SAT
        }
        
        # Extraer datos del Receptor
        receptor_data = comprobante.get("cfdi:Receptor", {})
        receptor = {
            "rfc": receptor_data.get("Rfc", ""),
            "nombre": receptor_data.get("Nombre", ""),
            "domicilio_fiscal": receptor_data.get("DomicilioFiscalReceptor", ""),
            "regimen_fiscal": ""  # Se obtendrá de la BD de catálogos SAT
        }
        
        # Extraer datos del Comprobante
        comprobante_info = {
            "tipo_comprobante": "",  # Se obtendrá de la BD de catálogos SAT
            "fecha": comprobante.get("Fecha", ""),
            "serie": comprobante.get("Serie", ""),
            "folio": comprobante.get("Folio", ""),
            "lugar_expedicion": comprobante.get("LugarExpedicion", "")
        }
        
        # Extraer Conceptos
        conceptos_data = comprobante.get("cfdi:Conceptos", {}).get("cfdi:Concepto", [])
        # Asegurar que conceptos_data sea una lista
        if not isinstance(conceptos_data, list):
            conceptos_data = [conceptos_data]
        
        conceptos = []
        for concepto in conceptos_data:
            conceptos.append({
                "no_identificacion": concepto.get("NoIdentificacion", ""),
                "descripcion": concepto.get("Descripcion", ""),
                "unidad": "",  # Se obtendrá de la BD de catálogos SAT (ClaveUnidad)/(Unidad)
                "cantidad": concepto.get("Cantidad", ""),
                "valor_unitario": concepto.get("ValorUnitario", ""),
                "importe": concepto.get("Importe", "")
            })
        
        # Extraer Sello del CFDI desde el XML sellado
        sello_cfdi = ""
        if xml_sellado:
            try:
                root = etree.fromstring(xml_sellado.encode('utf-8'))
                sello_cfdi = root.get('Sello', '')
            except Exception as e:
                print(f"[WARNING] No se pudo extraer el Sello del XML: {e}")
        
        # Datos de los Sellos Digitales
        sellos = {
            "cadena_original": cadena_original or "",
            "sello_cfdi": sello_cfdi,
            "sello_sat": ""  # Por ahora vacío, se agregará cuando esté disponible en Timbrado
        }
        
        return {
            "emisor": emisor,
            "receptor": receptor,
            "comprobante": comprobante_info,
            "conceptos": conceptos,
            "sellos": sellos
        }
    
    def generar_html(self, datos: dict) -> str:
        """
        Genera el HTML con los datos inyectados
        
        Args:
            datos: Diccionario con los datos organizados (resultado de extraer_datos_json)
            
        Returns:
            String con el HTML generado
        """
        html_generado = self.template.render(**datos)
        
        # Incrustar CSS inline para hacer el HTML portable
        css_content = self.leer_css()
        if css_content:
            # Reemplazar el link al CSS con un <style> inline
            html_generado = html_generado.replace(
                '<link rel="stylesheet" href="../css/PDF.css">',
                f'<style>\n{css_content}\n</style>'
            )
        
        return html_generado
    
    def generar_pdf_desde_json(self, datos_json: dict, xml_sellado: str = None, cadena_original: str = None, output_path: str = None) -> str:
        # Extraer datos del JSON
        datos_organizados = self.extraer_datos_json(datos_json, xml_sellado, cadena_original)
        
        # Generar HTML
        html_generado = self.generar_html(datos_organizados)
        
        # Guardar en archivo si se especifica ruta
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_generado)
            print(f"[INFO] HTML generado y guardado en: {output_path}")
        
        return html_generado


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de JSON de entrada (simplificado)
    ejemplo_json = {
        "datosXML": {
            "cfdi:Comprobante": {
                "Fecha": "2025-10-03T10:30:00",
                "Serie": "A",
                "Folio": "12345",
                "LugarExpedicion": "64000",
                "cfdi:Emisor": {
                    "Rfc": "AAA010101AAA",
                    "Nombre": "EMPRESA EJEMPLO SA DE CV"
                },
                "cfdi:Receptor": {
                    "Rfc": "XAXX010101000",
                    "Nombre": "PUBLICO EN GENERAL",
                    "DomicilioFiscalReceptor": "64000"
                },
                "cfdi:Conceptos": {
                    "cfdi:Concepto": [
                        {
                            "NoIdentificacion": "PROD001",
                            "Descripcion": "Producto de ejemplo",
                            "Cantidad": "10",
                            "ValorUnitario": "100.00",
                            "Importe": "1000.00"
                        }
                    ]
                }
            }
        }
    }
    
    # Crear inyector y generar HTML
    inyector = InyectorPDF()
    html_resultado = inyector.generar_pdf_desde_json(
        datos_json=ejemplo_json,
        cadena_original="||1.1|UUID|2025-10-03T10:30:00||...",
        output_path="resultado_ejemplo.html"
    )
    
    print("[INFO] Proceso completado exitosamente")