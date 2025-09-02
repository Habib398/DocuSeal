import json
from cryptography.fernet import Fernet

class InterpreteJson:
    def __init__(self, cadena_json: str, key: bytes):
        self.cadena_json = cadena_json
        self.fernet = Fernet(key)
        try:
            self.data = json.loads(cadena_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {e}")

        certificado = self.data.get("certificado", {})
        self._cer = self.fernet.encrypt(certificado.get("CER", "").encode())
        self._key = self.fernet.encrypt(certificado.get("KEY", "").encode())
        self._pwd_cer = self.fernet.encrypt(certificado.get("pwdCER", "").encode())

    def get_cer(self):
        return self.fernet.decrypt(self._cer).decode()

    def get_key(self):
        return self.fernet.decrypt(self._key).decode()

    def get_pwd_cer(self):
        return self.fernet.decrypt(self._pwd_cer).decode()

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