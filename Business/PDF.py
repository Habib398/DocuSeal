from CapaNegocio.PreferenciasCliente import PreferenciasCliente


class PDF:
    def __init__(self, solicitoPDF: PreferenciasCliente, idPDF: int, contenido: str):
        self.solicitoPDF = solicitoPDF.enviarPDF
        self.idPDF = idPDF
        self.contenido = contenido

    def GenerarPDF(self):
        # Lógica para generar el PDF
        pass