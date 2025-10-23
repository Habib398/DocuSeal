"""
ServicioTimbrarSellar.py - Service Layer para operaciones completas de sellado y timbrado
Acepta:
- "xml": string XML
- "datosXML": estructura JSON (dict)
"""

import logging
from typing import Dict, Any

from Business.cfdi import ComprobanteFactory
from .SellarXML import SellarXML
from .Timbrado import TimbradoService
from .PDF import PDF
from .PreferenciasCliente import PreferenciasCliente

logger = logging.getLogger(__name__)


class ServicioTimbrarSellar:
    """
    Servicio para operaciones completas de sellado y timbrado de CFDI desde XML.
    """
    
    @staticmethod
    def procesar(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un CFDI completo: sellado y timbrado.
        Acepta:
        - "xml": string XML
        - "datosXML": estructura JSON (dict)
        Requiere "claveUsuario" para obtener certificados de la BD.
        """
        logger.info("Iniciando proceso completo de timbrarSellar")
        
        # Validar claveUsuario
        clave_usuario = data.get('claveUsuario')
        if not clave_usuario:
            return {"error": "Falta el campo 'claveUsuario' en la petición"}
        
        # Validar que venga al menos uno de los dos formatos
        xml_input = data.get('xml')
        json_input = data.get('datosXML')
        
        if not xml_input and not json_input:
            return {"error": "Debe proporcionar 'xml' (string XML) o 'datosXML' (estructura JSON)"}
        
        if xml_input:
            logger.info(f"Procesando XML string (longitud: {len(xml_input)} caracteres)")
        else:
            logger.info("Procesando estructura JSON en 'datosXML'")
            # Validar JSON con ComprobanteFactory
            resultado_validacion = ComprobanteFactory.procesar_comprobante(json_input)
            if not resultado_validacion["valido"]:
                return {
                    "error": "Errores de validación en el comprobante",
                    "errores": resultado_validacion["errores"],
                    "warnings": resultado_validacion["warnings"]
                }
        
        # Obtener credenciales PAC de la base de datos usando claveUsuario
        from .Configuration.ConfiguracionCertificados import ConfiguracionCertificados
        from DB.DBManager import DBManager
        
        try:
            db_manager = DBManager()
            config_cert = ConfiguracionCertificados(db_manager)
            certificado = config_cert.obtener_por_clave_usuario(clave_usuario)
            
            if not certificado:
                return {
                    "error": "Certificado no encontrado",
                    "detalle": f"No se encontró certificado con claveUsuario {clave_usuario} en la base de datos"
                }
            
            usuario_pac = certificado.get('usuarioPAC')
            contrasena_pac = certificado.get('contrasenaPAC')
            
            if not usuario_pac or not contrasena_pac:
                return {
                    "error": "Credenciales PAC incompletas",
                    "detalle": f"El certificado {clave_usuario} no tiene usuarioPAC o contrasenaPAC configurados"
                }
            
            logger.info(f"Credenciales PAC obtenidas para claveUsuario: {clave_usuario}")
            
        except Exception as e:
            logger.error(f"Error al obtener credenciales PAC de la BD: {str(e)}")
            return {
                "error": "Error al acceder a la base de datos",
                "detalle": f"No se pudieron obtener las credenciales PAC: {str(e)}"
            }
        
        # Sellado (pasa claveUsuario)
        logger.info("Iniciando sellado")
        resultado_sellado = SellarXML.sellar_cfdi(data)
        if "error" in resultado_sellado:
            logger.error(f"Error en sellado: {resultado_sellado['error']}")
            return resultado_sellado
        
        xml_sellado = resultado_sellado["xml_con_sello"]
        cadena_original = resultado_sellado.get("cadena_original", "")
        logger.info(f"Cadena original generada: {cadena_original}")
        logger.info("Sellado exitoso")
        
        # IMPRIMIR XML GENERADO
        print("\n" + "="*80)
        print("XML SELLADO GENERADO:")
        print("="*80)
        print(xml_sellado)
        print("="*80 + "\n")
        
        pruebas = data.get("pruebas", True)
        
        # IMPRIMIR XML ANTES DE TIMBRAR
        print("\n" + "="*80)
        print("XML QUE SE ENVIARÁ AL PAC:")
        print("="*80)
        print(xml_sellado)
        print("="*80 + "\n")
        
        # Timbrado
        resultado_timbrado = TimbradoService.timbrar_cfdi(
            xml_sellado,
            usuario_pac,
            contrasena_pac,
            pruebas
        )
        
        # Preparar respuesta
        respuesta = resultado_timbrado.copy()
        logger.info("Timbrado exitoso")
        
        # Generar PDF solo si el timbrado fue exitoso y se solicita
        if "error" not in resultado_timbrado:
            preferencias = PreferenciasCliente.from_json(data)
            if preferencias.enviarPDF:
                uuid = resultado_timbrado.get("uuid", "temp")
                # Ahora solo necesitamos pasar el xml_sellado y uuid
                pdf_info = PDF.generar_desde_datos(xml_sellado, uuid)
                respuesta.update(pdf_info)
            else:
                respuesta["html_generado"] = False
        else:
            respuesta["html_generado"] = False
        
        return respuesta