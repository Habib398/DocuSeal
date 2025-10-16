import os
import sys
from typing import Optional, Tuple

# Añadir ruta al Frontend para acceder al Inyector
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_templates_path = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'Frontend', 'Templates'))
frontend_templates_file = os.path.join(frontend_templates_path, 'Inyector.py')

# Si existe, añadir al path para poder importar como módulo simple
if os.path.exists(frontend_templates_file):
    if frontend_templates_path not in sys.path:
        sys.path.insert(0, frontend_templates_path)
    from Inyector import InyectorPDF
else:
    # Fallback: intentar importar a través de ruta relativa si el paquete está instalado de otra forma
    try:
        from Frontend.Templates.Inyector import InyectorPDF
    except Exception:
        # Informar claramente del problema para facilitar debugging
        raise ImportError(f"No se encontró 'Inyector.py' en: {frontend_templates_file}. Asegúrate de que Frontend/Templates/Inyector.py existe y es accesible.")


class PDF:
    # metodo iniciador de la clase
    def __init__(self, datos_json: dict, xml_sellado: str, cadena_original: str, uuid: str = None):
        self.datos_json = datos_json
        self.xml_sellado = xml_sellado
        self.cadena_original = cadena_original
        self.uuid = uuid or "temp"
        self.html_generado = None
        self.html_path = None
        
        # Configurar directorio temporal
        self.temp_dir = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'Temp'))
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generar_html(self) -> Tuple[Optional[str], Optional[str]]:
        try:
            # Crear inyector
            inyector = InyectorPDF()
            
            # Definir nombre y ruta del archivo
            html_filename = f"comprobante_{self.uuid}.html"
            self.html_path = os.path.join(self.temp_dir, html_filename)
            
            # Generar HTML con los datos
            self.html_generado = inyector.generar_pdf_desde_json(
                datos_json=self.datos_json,
                xml_sellado=self.xml_sellado,
                cadena_original=self.cadena_original,
                output_path=self.html_path
            )
            
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
    
    @classmethod
    def generar_desde_datos(cls, datos_json: dict, xml_sellado: str, cadena_original: str, uuid: str = None) -> dict:
        pdf_generator = cls(datos_json, xml_sellado, cadena_original, uuid)
        html_generado, html_path = pdf_generator.generar_html()
        
        resultado = {}
        if html_generado and html_path:
            resultado["html_pdf_url"] = pdf_generator.obtener_url_visualizacion()
            resultado["html_pdf_path"] = html_path
            resultado["html_generado"] = True
        else:
            resultado["html_generado"] = False
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
