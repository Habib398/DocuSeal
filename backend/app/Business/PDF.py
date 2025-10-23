import os
from typing import Optional, Tuple
import base64

# Importar satcfdi para parsear y renderizar XML
from satcfdi.cfdi import CFDI
from satcfdi.render import html_str

# Importar para generar PDF desde HTML
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

current_dir = os.path.dirname(os.path.abspath(__file__))


class PDF:
    # metodo iniciador de la clase
    def __init__(self, xml_sellado: str, uuid: str = None):
        """
        Inicializa el generador de comprobante HTML usando satcfdi.
        
        Args:
            xml_sellado: String con el XML del CFDI sellado
            uuid: UUID del comprobante (opcional, se usa "temp" por defecto)
        """
        self.xml_sellado = xml_sellado
        self.uuid = uuid or "temp"
        self.html_generado = None
        self.html_path = None
        
        # Configurar directorio temporal
        self.temp_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'Temp'))
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generar_html(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Genera el HTML del comprobante usando satcfdi.render
        
        Returns:
            Tupla con (html_generado, html_path) o (None, None) en caso de error
        """
        try:
            # Parsear el XML usando satcfdi
            print("[INFO] Parseando XML con satcfdi...")
            cfdi = CFDI.from_string(self.xml_sellado.encode('utf-8'))
            
            # Generar HTML usando las plantillas de satcfdi
            print("[INFO] Generando HTML con plantillas satcfdi...")
            self.html_generado = html_str(cfdi)
            
            # Definir nombre y ruta del archivo
            html_filename = f"comprobante_{self.uuid}.html"
            self.html_path = os.path.join(self.temp_dir, html_filename)
            
            # Guardar el HTML generado
            with open(self.html_path, 'w', encoding='utf-8') as f:
                f.write(self.html_generado)
            
            print(f"[INFO] HTML del comprobante generado exitosamente en: {self.html_path}")
            return self.html_generado, self.html_path
            
        except Exception as e:
            print(f"[ERROR] Error al generar HTML del comprobante: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def obtener_url_visualizacion(self) -> Optional[str]:
        if self.html_path:
            return f"/ver-comprobante/{os.path.basename(self.html_path)}"
        return None
    
    def generar_pdf_base64(self) -> Optional[str]:
        """
        Genera un PDF desde el HTML usando pdfkit y lo devuelve como base64.
        
        Returns:
            String con el PDF en base64, o None si falla
        """
        if not PDFKIT_AVAILABLE:
            print("[WARNING] pdfkit no está disponible. Instala con: pip install pdfkit")
            return None
        
        try:
            # Verificar que wkhtmltopdf esté disponible
            try:
                pdfkit.from_string("<html><body>Test</body></html>", False)
            except OSError as e:
                print(f"[ERROR] wkhtmltopdf no está instalado o no es accesible: {e}")
                print("[INFO] Descarga wkhtmltopdf desde: https://wkhtmltopdf.org/downloads.html")
                return None
            
            # Configurar opciones de pdfkit para mejor calidad
            options = {
                'page-size': 'Letter',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': 'UTF-8',
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            # Generar PDF como bytes usando pdfkit
            print("[INFO] Generando PDF con pdfkit...")
            pdf_bytes = pdfkit.from_string(self.html_generado, False, options=options)
            
            # Convertir a base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            print(f"[INFO] PDF generado correctamente ({len(pdf_bytes)} bytes, base64: {len(pdf_base64)} chars)")
            return pdf_base64
            
        except Exception as e:
            print(f"[ERROR] Error al generar PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @classmethod
    def generar_desde_datos(cls, xml_sellado: str, uuid: str = None) -> dict:
        """
        Método de clase para generar un comprobante HTML y PDF desde XML sellado.
        
        Args:
            xml_sellado: String con el XML del CFDI sellado
            uuid: UUID del comprobante (opcional)
            
        Returns:
            Diccionario con información sobre el resultado de la generación
        """
        pdf_generator = cls(xml_sellado, uuid)
        html_generado, html_path = pdf_generator.generar_html()
        
        resultado = {}
        if html_generado and html_path:
            resultado["html_pdf_url"] = pdf_generator.obtener_url_visualizacion()
            resultado["html_pdf_path"] = html_path
            resultado["html_generado"] = True
            
            # Generar PDF base64
            pdf_base64 = pdf_generator.generar_pdf_base64()
            if pdf_base64:
                resultado["pdf_base64"] = pdf_base64
                resultado["pdf_generado"] = True
            else:
                resultado["pdf_generado"] = False
                resultado["error_pdf"] = "No se pudo generar el PDF"
        else:
            resultado["html_generado"] = False
            resultado["pdf_generado"] = False
            resultado["error_html"] = "No se pudo generar el HTML del comprobante"
        
        return resultado
    
    @staticmethod
    def obtener_ruta_comprobante(filename: str) -> Optional[str]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'Temp'))
        html_path = os.path.join(temp_dir, filename)
        
        if os.path.exists(html_path):
            return html_path
        return None
    
    @staticmethod
    def leer_comprobante(filename: str) -> Optional[str]:
        html_path = PDF.obtener_ruta_comprobante(filename)
        if html_path:
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"[ERROR] Error al leer el comprobante: {e}")
                return None
        return None
    
    def GenerarPDF(self):
        return self.generar_html()
