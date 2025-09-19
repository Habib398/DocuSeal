from cryptography.fernet import Fernet
import json

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
        return self.fernet.decrypt(self._cer).decode()

    def get_key(self):
        return self.fernet.decrypt(self._key).decode()

    def get_pwd_cer(self):
        return self.fernet.decrypt(self._pwd_cer).decode()