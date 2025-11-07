"""
ServicioCancelacion.py - Service Layer para operaciones de cancelación de CFDI
Maneja la lógica de negocio y coordina con la base de datos para cancelar comprobantes.
"""

import logging
from typing import Dict, Any
from Business.Cancelacion import CancelacionService
from Business.Configuration.ConfiguracionCertificados import ConfiguracionCertificados
from DB.DBManager import DBManager

logger = logging.getLogger(__name__)


class ServicioCancelacion:
    """
    Servicio para operaciones de cancelación de CFDI.
    Obtencion de certificados desde BD y coordinación con el PAC.
    """
    
    @staticmethod
    def cancelar(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancela uno o más CFDI usando el web service del PAC.
        """
        # Validar claveUsuario
        clave_usuario = data.get('claveUsuario')
        if not clave_usuario:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "CAN001",
                    "mensaje": "Falta campo 'claveUsuario' en el cuerpo de la petición"
                }]
            }
        
        # Validar folios
        folios = data.get('folios')
        if not folios or not isinstance(folios, list) or len(folios) == 0:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "CAN002",
                    "mensaje": "Falta campo 'folios' o está vacío. Debe ser una lista con al menos un folio"
                }]
            }
        
        # Obtener certificado de la base de datos
        try:
            db_manager = DBManager()
            config_cert = ConfiguracionCertificados(db_manager)
            certificado = config_cert.obtener_por_clave_usuario(clave_usuario)
            
            if not certificado:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "CAN003",
                        "mensaje": "Certificado no encontrado",
                        "detalle": f"No se encontró certificado con claveUsuario {clave_usuario} en la base de datos"
                    }]
                }
            
            # Obtener credenciales PAC y certificados de la BD
            usuario_pac = certificado.get('usuarioPAC')
            contrasena_pac = certificado.get('contrasenaPAC')
            certificado_base64 = certificado.get('CER')
            llave_base64 = certificado.get('KEY')
            contrasena_llave = certificado.get('pwdCER')

            # Validar que existan datos necesarios
            if not usuario_pac or not contrasena_pac:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "CAN004",
                        "mensaje": "Credenciales PAC incompletas",
                        "detalle": f"El certificado {clave_usuario} no tiene usuarioPAC o contrasenaPAC configurados"
                    }]
                }
            
            if not certificado_base64 or not llave_base64:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "CAN005",
                        "mensaje": "Certificados faltantes",
                        "detalle": f"El certificado {clave_usuario} no tiene los archivos .cer o .key en base64"
                    }]
                }
            
            if not contrasena_llave:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "CAN006",
                        "mensaje": "Contraseña de llave faltante",
                        "detalle": f"El certificado {clave_usuario} no tiene contrasenaLlave configurada"
                    }]
                }
            
        except Exception as e:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "CAN007",
                    "mensaje": "Error al acceder a la base de datos",
                    "detalle": f"No se pudo obtener el certificado: {str(e)}"
                }]
            }
        
        # Obtener el modo de pruebas desde el certificado
        pruebas = certificado.get('pruebas', True)
        
        # Obtener parámetros opcionales
        email_emisor = data.get('emailEmisor')
        email_receptor = data.get('emailReceptor')
        guardar_acuse = data.get('guardarAcuse', True)

        # Procesar folio
        resultados = []
        for folio in folios:
            try:
                # Validar campos requeridos del folio
                uuid = folio.get('uuid')
                rfc_receptor = folio.get('rfcReceptor')
                total = folio.get('total')
                tipo_comprobante = folio.get('tipoComprobante')
                motivo = folio.get('motivo')
                folio_sustitucion = folio.get('folioSustitucion')
                
                if not uuid:
                    resultados.append({
                        "codigo": -1,
                        "mensaje": "Folio inválido: falta campo 'uuid'",
                        "uuid": None,
                        "error": "Campo 'uuid' requerido"
                    })
                    continue
                
                if not rfc_receptor:
                    resultados.append({
                        "codigo": -1,
                        "mensaje": "Folio inválido: falta campo 'rfcReceptor'",
                        "uuid": uuid,
                        "error": "Campo 'rfcReceptor' requerido"
                    })
                    continue
                
                if not total:
                    resultados.append({
                        "codigo": -1,
                        "mensaje": "Folio inválido: falta campo 'total'",
                        "uuid": uuid,
                        "error": "Campo 'total' requerido"
                    })
                    continue
                
                if not tipo_comprobante:
                    resultados.append({
                        "codigo": -1,
                        "mensaje": "Folio inválido: falta campo 'tipoComprobante'",
                        "uuid": uuid,
                        "error": "Campo 'tipoComprobante' requerido"
                    })
                    continue
                
                if not motivo:
                    resultados.append({
                        "codigo": -1,
                        "mensaje": "Folio inválido: falta campo 'motivo'",
                        "uuid": uuid,
                        "error": "Campo 'motivo' requerido"
                    })
                    continue
                
                # Llamar al servicio de cancelación
                resultado = CancelacionService.cancelar_uuid(
                    uuid=uuid,
                    rfc_receptor=rfc_receptor,
                    total=str(total),
                    tipo_comprobante=tipo_comprobante,
                    motivo=motivo,
                    usuario_pac=usuario_pac,
                    password_pac=contrasena_pac,
                    certificado_base64=certificado_base64,
                    key_base64=llave_base64,
                    password_key=contrasena_llave,
                    uuid_relacionado=folio_sustitucion,
                    email_emisor=email_emisor,
                    email_receptor=email_receptor,
                    guardar_acuse=guardar_acuse,
                    pruebas=pruebas
                )
                
                resultados.append(resultado)
                
            except Exception as e:
                logger.exception(f"Error al procesar folio: {folio}")
                resultados.append({
                    "codigo": -1,
                    "mensaje": "Error al procesar folio",
                    "uuid": folio.get('uuid'),
                    "error": "Error inesperado",
                    "detalle": str(e)
                })
        
        # retornar resultado directo si solo hay un folio
        if len(folios) == 1:
            return resultados[0]
        
        # retornar resumen si hay lista de folios
        from ResultadoCancelacion import ResultadoCancelacion
        return ResultadoCancelacion.ResultadoMultiple(resultados)
