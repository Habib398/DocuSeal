import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.x509 import load_der_x509_certificate

class VerificadorSello:
    @staticmethod
    def verificar_sello(cadena_original: str, sello: str, cer_path: str) -> bool:
        """
        Verifica si el sello digital es correcto usando la cadena original y el certificado.
        Args:
            cadena_original (str): La cadena original generada del XML.
            sello (str): El sello digital en base64.
            cer_path (str): Ruta al archivo .cer (certificado).
        Returns:
            bool: True si el sello es válido, False si no.
        """
        try:
            # Cargar el certificado y obtener la llave pública
            with open(cer_path, 'rb') as f:
                cert_data = f.read()
            cert = load_der_x509_certificate(cert_data)
            public_key = cert.public_key()

            # Decodificar el sello
            sello_bytes = base64.b64decode(sello)

            # Verificar la firma
            public_key.verify(
                sello_bytes,
                cadena_original.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            # Si hay error, el sello no es válido
            return False
