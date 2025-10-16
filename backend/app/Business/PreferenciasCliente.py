class PreferenciasCliente:
    def __init__(self, idPreferencia: int = None, enviarEmail: bool = False, enviarPDF: bool = False):
        self.idPreferencia = idPreferencia
        self.enviarEmail = bool(enviarEmail)
        self.enviarPDF = bool(enviarPDF)

    @classmethod
    def from_json(cls, data: dict) -> "PreferenciasCliente":
        # Leer enviarCorreo
        enviar_email = data.get("enviarCorreo")
        if enviar_email is None:
            enviar_email = data.get("enviarEmail", False)
        
        # Leer generarPDF
        generar_pdf = data.get("generarPDF")
        if generar_pdf is None:
            generar_pdf = data.get("enviarPDF", False)
        
        return cls(
            enviarEmail=enviar_email,
            enviarPDF=generar_pdf
        )