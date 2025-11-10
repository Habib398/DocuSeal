"""
SellarXML.py - Clase para el sellado de CFDI
Maneja el sellado criptográfico de documentos CFDI usando certificados de la base de datos.
"""

import logging
from typing import Optional
from DB.DBManager import DBManager
import base64
from satcfdi.models import Signer
from satcfdi.cfdi import CFDI

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SellarXML:
    """
    Clase para el sellado de documentos CFDI.
    Obtiene los certificados CER y KEY desde la base de datos y realiza el sellado digital.
    """

    def __init__(self, id: int, xml: str, cer_bytes: bytes, key_bytes: bytes, password: Optional[str] = None, xmlSellado: Optional[str] = None):
        self.id = id
        self.xml = xml
        self.cer_bytes = cer_bytes
        self.key_bytes = key_bytes
        self.password = password
        self.xmlSellado = xmlSellado
        self.cadena_original: Optional[str] = None

    def get_sello(self) -> str:
        """Retorna el XML sellado"""
        return self.xmlSellado
    
    def get_cadena_original(self) -> Optional[str]:
        """Retorna la cadena original generada durante el sellado"""
        return self.cadena_original

    @staticmethod
    def obtener_datos_certificado_por_clave(claveUsuario: str) -> Optional[dict]:
        """
        Obtiene todos los datos del certificado usando claveUsuario.
        """
        from .Configuration.ConfiguracionCertificados import ConfiguracionCertificados
        
        db = DBManager()
        config_cert = ConfiguracionCertificados(db)
        certificado = config_cert.obtener_por_clave_usuario(claveUsuario)
        
        if not certificado:
            logger.warning(f"No se encontró certificado con claveUsuario: {claveUsuario}")
            return None
        
        logger.info(f"Certificado encontrado para claveUsuario: {claveUsuario}")
        logger.debug(f"Datos del certificado: {certificado.keys()}")
        
        # Decodificar CER y KEY de base64 a bytes
        cer_b64 = certificado.get('CER')
        key_b64 = certificado.get('KEY')
        
        logger.debug(f"CER presente: {cer_b64 is not None}, KEY presente: {key_b64 is not None}")
        if cer_b64:
            logger.debug(f"CER longitud base64: {len(cer_b64)}")
        if key_b64:
            logger.debug(f"KEY longitud base64: {len(key_b64)}")
        
        try:
            cer_bytes = base64.b64decode(cer_b64) if cer_b64 else None
            key_bytes = base64.b64decode(key_b64) if key_b64 else None
            
            if cer_bytes:
                logger.debug(f"CER decodificado a bytes, longitud: {len(cer_bytes)}")
            if key_bytes:
                logger.debug(f"KEY decodificado a bytes, longitud: {len(key_bytes)}")
                
        except Exception as e:
            logger.error(f"Error decodificando CER/KEY: {str(e)}")
            raise ValueError(f"Error decodificando CER/KEY: {str(e)}")
        
        return {
            'cer_bytes': cer_bytes,
            'key_bytes': key_bytes,
            'certificado_texto': certificado.get('Certificado'),
            'pwd_cer': certificado.get('pwdCER', ''),
            'no_certificado': certificado.get('noCertificado')
        }

    @staticmethod
    def obtener_cer_db(noCertificado: str) -> Optional[bytes]:
        """
        Obtiene el campo CER de la base de datos en formato bytes.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            cer_b64 = registro.get('CER')
            if cer_b64:
                try:
                    return base64.b64decode(cer_b64)
                except Exception as e:
                    raise ValueError(f"Error decodificando CER: {str(e)}")
        return None

    @staticmethod
    def obtener_key_db(noCertificado: str) -> Optional[bytes]:
        """
        Obtiene el campo KEY de la base de datos en formato bytes.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            key_b64 = registro.get('KEY')
            if key_b64:
                try:
                    return base64.b64decode(key_b64)
                except Exception as e:
                    raise ValueError(f"Error decodificando KEY: {str(e)}")
        return None

    @staticmethod
    def obtener_certificado_db(noCertificado: str) -> Optional[str]:
        """
        Obtiene el campo Certificado (texto base64) de la base de datos.
        Este campo contiene el certificado en formato base64 tal como se usa en el XML.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            return registro.get('Certificado')
        return None

    @staticmethod
    def obtener_password_db(noCertificado: str) -> str:
        """
        Obtiene la contraseña del certificado desde la base de datos.
        """
        db = DBManager()
        registro = db.get_certificado_by_noCertificado(noCertificado)
        if registro:
            pwd = registro.get('pwdCER')
            return pwd if pwd else ''
        return ''
    
    def _load_signer(self) -> Signer:
        """
        Carga el signer (firmador) usando los certificados en bytes.
        """
        return Signer.load(
            certificate=self.cer_bytes, 
            key=self.key_bytes, 
            password=self.password
        )
    
    @classmethod
    def sellar_cfdi(cls, data: dict) -> dict:
        """
        Método principal para sellar un CFDI.
        Requiere claveUsuario para obtener los certificados de la BD.
        Acepta:
        - "xml": string XML
        - "datosXML": estructura JSON (dict)
        - "claveUsuario": clave única del certificado
        """
        try:
            # Validar que venga claveUsuario
            clave_usuario = data.get("claveUsuario")
            if not clave_usuario:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML001",
                        "mensaje": "Falta el campo 'claveUsuario' en la petición"
                    }]
                }
            
            # Verificar qué formato viene
            xml_string_input = data.get("xml")
            json_input = data.get("datosXML")
            
            # CASO 1: Viene como estructura JSON en "datosXML"
            if json_input and isinstance(json_input, dict):
                
                    # Convertir JSON a XML usando ConvertirJson
                    from .cfdi.ConvertirJson import ConvertirJson
                    try:
                        converter = ConvertirJson()
                        cfdi_obj = converter.convertir_a_cfdi(json_input)
                        xml_element = cfdi_obj.to_xml()
                        from lxml import etree
                        xml_input = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
                    except Exception as e:
                        return {
                            "errores": [{
                                "tipo": "error",
                                "codigo": "SXML002",
                                "mensaje": f"Error al convertir JSON a XML: {str(e)}"
                            }]
                        }            # CASO 2: Viene como XML string en "xml"
            elif xml_string_input and isinstance(xml_string_input, str):
                xml_input = xml_string_input.strip()
                
                # Verificar si es un comprobante de pago y convertir a JSON para procesar correctamente
                from lxml import etree
                try:
                    xml_tree = etree.fromstring(xml_input.encode('utf-8'))
                    tipo_comprobante = xml_tree.get('TipoDeComprobante')
                    if tipo_comprobante == 'P':
                        # Convertir XML de pago a estructura JSON
                        json_input = cls._xml_pago_a_json(xml_tree)
                        # Procesar como JSON
                        from .cfdi.ConvertirJson import ConvertirJson
                        converter = ConvertirJson()
                        cfdi_obj = converter.convertir_a_cfdi(json_input)
                        xml_element = cfdi_obj.to_xml()
                        from lxml import etree
                        xml_input = etree.tostring(xml_element, encoding='unicode', pretty_print=True)
                    # Para otros tipos, continuar con XML directo
                except Exception as e:
                    return {
                        "errores": [{
                            "tipo": "error",
                            "codigo": "SXML010",
                            "mensaje": f"Error al procesar XML de pago: {str(e)}"
                        }]
                    }
            
            # CASO 3: No viene ninguno de los dos formatos válidos
            else:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML003",
                        "mensaje": "Debe proporcionar 'xml' (string XML) o 'datosXML' (estructura JSON)"
                    }]
                }
            
            # Limpiar y normalizar el XML (eliminar espacios/saltos de línea innecesarios)
            import re
            xml_input = re.sub(r'>\s+<', '><', xml_input)
            
            # Obtener datos del certificado usando claveUsuario
            datos_cert = cls.obtener_datos_certificado_por_clave(clave_usuario)
            if not datos_cert:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML004",
                        "mensaje": f"No se encontró certificado con claveUsuario: {clave_usuario}"
                    }]
                }
            
            cer_bytes = datos_cert['cer_bytes']
            key_bytes = datos_cert['key_bytes']
            certificado_texto = datos_cert['certificado_texto']
            pwd_cer = datos_cert['pwd_cer']
            no_certificado = datos_cert['no_certificado']
            
            if not cer_bytes or not key_bytes:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML005",
                        "mensaje": "No se encontraron CER o KEY en la base de datos para el certificado proporcionado."
                    }]
                }
            
            if not certificado_texto:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML006",
                        "mensaje": "No se encontró el campo Certificado en la base de datos para el certificado proporcionado."
                    }]
                }
            
            if not no_certificado:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML007",
                        "mensaje": "No se encontró el noCertificado en la base de datos."
                    }]
                }
            
            # Parsear XML y actualizar campos desde la BD
            from lxml import etree
            try:
                xml_tree = etree.fromstring(xml_input.encode('utf-8'))
            except Exception as e:
                return {
                    "errores": [{
                        "tipo": "error",
                        "codigo": "SXML008",
                        "mensaje": f"Error al parsear XML: {str(e)}"
                    }]
                }

            # Establecer NoCertificado y Certificado desde la base de datos
            xml_tree.set('NoCertificado', no_certificado)
            xml_tree.set('Certificado', certificado_texto)
            xml_generado = etree.tostring(xml_tree, encoding='utf-8', xml_declaration=True).decode('utf-8')

            # Crear sellador con los bytes obtenidos de la BD
            sellador = cls(
                id=1,
                xml=xml_generado,
                cer_bytes=cer_bytes,
                key_bytes=key_bytes,
                password=pwd_cer
            )
            
            # Generar sello
            xml_con_sello = sellador.GenerarSello()
            
            return {
                "xml_con_sello": xml_con_sello
            }
                
        except Exception as e:
            return {
                "errores": [{
                    "tipo": "error",
                    "codigo": "SXML009",
                    "mensaje": f"Error general en el proceso de sellado: {str(e)}"
                }]
            }

    def GenerarSello(self) -> str:
        """
        Genera el sello digital del CFDI.
        """
        # Agregar atributo sello si no existe en xml
        from lxml import etree
        xml_tree = etree.fromstring(self.xml.encode('utf-8'))
        if 'Sello' not in xml_tree.attrib:
            xml_tree.set('Sello', '')
        self.xml = etree.tostring(xml_tree, encoding='utf-8', xml_declaration=True).decode('utf-8')

        # Crear CFDI y firmar
        cfdi = CFDI.from_string(self.xml.encode('utf-8'))
        signer = self._load_signer()
        cfdi.sign(signer)

        # Guardar la cadena original generada
        self.cadena_original = cfdi.cadena_original()

        # Generar XML sellado
        self.xmlSellado = cfdi.xml_bytes(pretty_print=True).decode('utf-8')
        return self.xmlSellado
    
    @classmethod
    def _xml_pago_a_json(cls, xml_tree) -> dict:
        """
        Convierte un XML de comprobante de pago a estructura JSON para procesar correctamente.
        """
        from lxml import etree
        
        # Extraer atributos del comprobante
        comprobante_data = dict(xml_tree.attrib)
        
        # Extraer emisor
        emisor_elem = xml_tree.find('.//{http://www.sat.gob.mx/cfd/4}Emisor')
        if emisor_elem is not None:
            comprobante_data['cfdi:Emisor'] = dict(emisor_elem.attrib)
        
        # Extraer receptor
        receptor_elem = xml_tree.find('.//{http://www.sat.gob.mx/cfd/4}Receptor')
        if receptor_elem is not None:
            comprobante_data['cfdi:Receptor'] = dict(receptor_elem.attrib)
        
        # Extraer complemento de pago
        complemento_data = {}
        pagos_elem = xml_tree.find('.//{http://www.sat.gob.mx/Pagos20}Pagos')
        if pagos_elem is not None:
            pagos_data = []
            for pago_elem in pagos_elem.findall('.//{http://www.sat.gob.mx/Pagos20}Pago'):
                pago_dict = dict(pago_elem.attrib)
                doctos = []
                for docto_elem in pago_elem.findall('.//{http://www.sat.gob.mx/Pagos20}DoctoRelacionado'):
                    docto_dict = dict(docto_elem.attrib)
                    # Extraer ImpuestosDR si existe
                    impuestos_elem = docto_elem.find('.//{http://www.sat.gob.mx/Pagos20}ImpuestosDR')
                    if impuestos_elem is not None:
                        impuestos_dict = {}
                        traslados_elem = impuestos_elem.find('.//{http://www.sat.gob.mx/Pagos20}TrasladosDR')
                        if traslados_elem is not None:
                            traslados = []
                            for traslado_elem in traslados_elem.findall('.//{http://www.sat.gob.mx/Pagos20}TrasladoDR'):
                                traslados.append(dict(traslado_elem.attrib))
                            if traslados:
                                impuestos_dict['TrasladosDR'] = traslados
                        retenciones_elem = impuestos_elem.find('.//{http://www.sat.gob.mx/Pagos20}RetencionesDR')
                        if retenciones_elem is not None:
                            retenciones = []
                            for retencion_elem in retenciones_elem.findall('.//{http://www.sat.gob.mx/Pagos20}RetencionDR'):
                                retenciones.append(dict(retencion_elem.attrib))
                            if retenciones:
                                impuestos_dict['RetencionesDR'] = retenciones
                        if impuestos_dict:
                            docto_dict['ImpuestosDR'] = impuestos_dict
                    doctos.append(docto_dict)
                pago_dict['DoctoRelacionado'] = doctos
                pagos_data.append(pago_dict)
            complemento_data['pago20'] = {'Pago': pagos_data}
        
        return {
            'datosXML': {
                'cfdi:Comprobante': comprobante_data,
                'complemento': complemento_data
            }
        }
