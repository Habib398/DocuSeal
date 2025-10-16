import json

class InterpreteJson:
    def __init__(self, cadena_json: str):
        # Convierte a diccionario la cadena JSON
        self.cadena_json = cadena_json
        try:
            self.data = json.loads(cadena_json)
            # Validar si es formato Json correcto
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {e}")

        # Preferencias cliente
        self.enviar_correo = self.data.get("enviarCorreo")
        self.generar_pdf = self.data.get("generarPDF")
        self.complemento = self.data.get("complemento")

        # XML - Puede venir como "datosXML" (estructura JSON) o "xml" (string)
        self.jsonData: dict = self.data.get("datosXML", {})
        self.conceptos: list = self.jsonData.get("conceptos", [])