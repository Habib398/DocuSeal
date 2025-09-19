from CapaNegocio.PreferenciasCliente import PreferenciasCliente


class Correo:
    def __init__(self, idCorreo: int, solicitoCorreo: PreferenciasCliente, destinatario: str, asunto: str, cuerpo: str):
        self.solicitoCorreo = solicitoCorreo.enviarEmail
        self.idCorreo = idCorreo
        self.destinatario = destinatario
        self.asunto = asunto
        self.cuerpo = cuerpo

    def GenerarCorreo(self):
        # Lógica para generar el contenido del correo
        pass

    def EnviarCorreo(self):
        # Lógica para enviar el correo
        pass
