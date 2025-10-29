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
            cfdi = CFDI.from_string(self.xml_sellado.encode('utf-8'))
            
            # Generar HTML usando las plantillas de satcfdi
            self.html_generado = html_str(cfdi)
            
            # No guardar archivo HTML en disco para hacerlo temporal
            self.html_path = None
            
            return self.html_generado, self.html_path
            
        except Exception as e:
            return None, None
    
    def generar_pdf_base64(self) -> Optional[str]:
        """
        Genera un PDF desde el HTML usando pdfkit y lo devuelve como base64
        Nota: Requiere que wkhtmltopdf esté instalado en la ruta por defecto del instalador.
        """
        if not PDFKIT_AVAILABLE:
            return None
        
        try:
            # Configurar la ruta a wkhtmltopdf
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            
            # Verificar que wkhtmltopdf esté disponible
            try:
                pdfkit.from_string("<html><body>Test</body></html>", False, configuration=config)
            except OSError as e:
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
            pdf_bytes = pdfkit.from_string(self.html_generado, False, options=options, configuration=config)
            
            # Convertir a base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            return pdf_base64
            
        except Exception as e:
            return None
    
    @classmethod
    def generar_desde_datos(cls, xml_sellado: str, uuid: str = None) -> dict:
        """
        Método de clase para generar un comprobante HTML y PDF desde XML sellado.
        """
        pdf_generator = cls(xml_sellado, uuid)
        html_generado, html_path = pdf_generator.generar_html()
        
        resultado = {}
        if html_generado:
            # Generar PDF base64
            pdf_base64 = pdf_generator.generar_pdf_base64()
            if pdf_base64:
                resultado["pdf_base64"] = pdf_base64
            else:
                resultado["pdf_generado"] = False
                resultado["error_pdf"] = "No se pudo generar el PDF"
        else:
            resultado["pdf_generado"] = False
            resultado["error_html"] = "No se pudo generar el HTML del comprobante"
        
        return resultado