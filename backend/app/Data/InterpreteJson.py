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

        # Configuracion sello
        certificado = self.data.get("certificado", {})
        self.cer = certificado.get("CER")
        self.key = certificado.get("KEY")
        self.pwd_cer = certificado.get("pwdCER")

        # Configuracion PAC
        pac = self.data.get("PAC", {})
        self.usuario_pac = pac.get("usuario")
        self.contrasena_pac = pac.get("contrasena")

        # XML
        self.jsonData: dict = self.data.get("datosXML", {})
        self.conceptos: list = self.jsonData.get("conceptos", [])