class PreferenciasCliente:
    def __init__(self, idPreferencia: int, enviarEmail: bool, enviarPDF: bool):
        self.idPreferencia = idPreferencia
        self.enviarEmail = enviarEmail
        self.enviarPDF = enviarPDF