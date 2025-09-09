class TimbradoError:
    def __init__(self,idTimbradoError: int, codigo: int, mensaje: str):
        self.idTimbradoError = idTimbradoError
        self.codigo = codigo
        self.mensaje = mensaje

    def GenerarResultadoError(self):
        # Devuelve el resultado de error en formato dict
        return {
            "id": self.idTimbradoError,
            "exito": False,
            "codigo": self.codigo,
            "mensaje": self.mensaje,
        }