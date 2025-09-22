from cryptography.fernet import Fernet
import json
import os

class ConfiguracionSello:
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
        cer_value = self.fernet.decrypt(self._cer).decode()
        # Si parece ser una ruta de archivo, devolverla tal como está
        if os.path.exists(cer_value) or (len(cer_value) < 500 and ('/' in cer_value or '\\' in cer_value)):
            return cer_value
        # Si no, es contenido base64, devolverlo tal como está
        return cer_value

    def get_key(self):
        key_value = self.fernet.decrypt(self._key).decode()
        # Si parece ser una ruta de archivo, devolverla tal como está
        if os.path.exists(key_value) or (len(key_value) < 500 and ('/' in key_value or '\\' in key_value)):
            return key_value
        # Si no, es contenido base64, devolverlo tal como está
        return key_value

    def get_pwd_cer(self):
        return self.fernet.decrypt(self._pwd_cer).decode()