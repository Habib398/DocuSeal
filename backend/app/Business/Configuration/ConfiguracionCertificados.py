"""
Módulo de configuración y lógica para la gestión de certificados PAC.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfiguracionCertificados:
    """Clase para manejar la lógica de gestión de certificados PAC."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    @staticmethod
    def extraer_info_certificado(cer_bytes: bytes) -> Dict[str, str]:
        """
        Extrae información del certificado .cer (noCertificado y vigencia).
        
        Args:
            cer_bytes: Contenido del archivo .cer en bytes (formato DER)
        
        Returns:
            dict con 'noCertificado' (serial number en formato SAT de 20 dígitos) y 'vigencia' (fecha expiración YYYY-MM-DD)
        
        Raises:
            ValueError: Si el certificado no se puede parsear
        """
        try:
            # Cargar el certificado en formato DER
            cert = x509.load_der_x509_certificate(cer_bytes, default_backend())
            
            # Extraer serial number en formato hexadecimal
            serial_hex = format(cert.serial_number, 'x')
            
            # El SAT requiere el número de serie en formato de 20 dígitos
            # El número hexadecimal debe convertirse a ASCII de cada par de caracteres
            # Ejemplo: "3330303031303030303030333030303233373038" -> "30001000000300023708"
            
            # Asegurar que el hex tenga un número par de caracteres
            if len(serial_hex) % 2 != 0:
                serial_hex = '0' + serial_hex
            
            # Convertir hex a string ASCII (cada par de caracteres hex representa un byte ASCII)
            try:
                no_certificado = bytes.fromhex(serial_hex).decode('ascii')
            except (ValueError, UnicodeDecodeError):
                # Si no se puede decodificar como ASCII, usar el hex directamente
                # Esto puede pasar con certificados que no siguen el estándar del SAT
                no_certificado = serial_hex.upper()
                logger.warning(f"No se pudo decodificar el serial como ASCII, usando hex: {no_certificado}")
            
            # Extraer fecha de expiración (vigencia) usando la nueva API
            try:
                # Usar not_valid_after_utc si está disponible (cryptography >= 42.0)
                not_after = cert.not_valid_after_utc
            except AttributeError:
                # Fallback para versiones anteriores
                not_after = cert.not_valid_after
            
            vigencia = not_after.strftime('%Y-%m-%d')
            
            logger.info(f"Información extraída del certificado: noCertificado={no_certificado}, vigencia={vigencia}")
            
            return {
                'noCertificado': no_certificado,
                'vigencia': vigencia
            }
        except Exception as e:
            logger.error(f"Error al extraer información del certificado: {e}")
            raise ValueError(f"No se pudo leer el certificado .cer: {str(e)}")
    
    def obtener_todos(self) -> List[Dict[str, Any]]:
        # Obtiene todos los certificados almacenados.
        try:
            certificados = self.db_manager.get_all_certificados()
            logger.info(f"Se obtuvieron {len(certificados)} certificados")
            return certificados
        except Exception as e:
            logger.error(f"Error obteniendo todos los certificados: {e}")
            raise RuntimeError(f"Error al obtener certificados: {str(e)}")
    
    def obtener_por_usuario(self, usuario_pac: str) -> Optional[Dict[str, Any]]:
        # Obtiene un certificado por usuario PAC.
        
        if not usuario_pac or not usuario_pac.strip():
            raise ValueError("El usuario PAC no puede estar vacío")
        
        try:
            certificado = self.db_manager.get_certificado_by_usuario(usuario_pac)
            
            if certificado:
                logger.info(f"Certificado encontrado para usuario: {usuario_pac}")
            else:
                logger.info(f"No se encontró certificado para usuario: {usuario_pac}")
            
            return certificado
        except Exception as e:
            logger.error(f"Error obteniendo certificado por usuario: {e}")
            raise RuntimeError(f"Error al buscar certificado: {str(e)}")
    
    def obtener_por_numero(self, no_certificado: str) -> Optional[Dict[str, Any]]:
        # Obtiene un certificado por número de certificado.

        if not no_certificado or not no_certificado.strip():
            raise ValueError("El número de certificado no puede estar vacío")
        
        try:
            certificado = self.db_manager.get_certificado_by_noCertificado(no_certificado)
            
            if certificado:
                logger.info(f"Certificado encontrado con número: {no_certificado}")
            else:
                logger.info(f"No se encontró certificado con número: {no_certificado}")
            
            return certificado
        except Exception as e:
            logger.error(f"Error obteniendo certificado por número: {e}")
            raise RuntimeError(f"Error al buscar certificado: {str(e)}")
    
    def obtener_por_clave_usuario(self, clave_usuario: str) -> Optional[Dict[str, Any]]:
        """Obtiene un certificado por claveUsuario única."""
        if not clave_usuario or not clave_usuario.strip():
            raise ValueError("La clave de usuario no puede estar vacía")
        
        try:
            certificado = self.db_manager.get_certificado_by_claveUsuario(clave_usuario)
            
            if certificado:
                logger.info(f"Certificado encontrado con claveUsuario: {clave_usuario}")
            else:
                logger.info(f"No se encontró certificado con claveUsuario: {clave_usuario}")
            
            return certificado
        except Exception as e:
            logger.error(f"Error obteniendo certificado por claveUsuario: {e}")
            raise RuntimeError(f"Error al buscar certificado: {str(e)}")
    
    def validar_datos_certificado(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> tuple[bool, str]:
        # Valida los datos de un certificado antes de crear o actualizar.
        
        if not es_actualizacion:
            # Validar campos requeridos solo en creación
            # noCertificado y vigencia son opcionales (se extraen del CER automáticamente)
            # Certificado NO es requerido, se genera automáticamente desde CER
            campos_requeridos = ['usuarioPAC', 'contrasenaPAC', 'CER', 'KEY', 'pwdCER']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or datos[campo] is None]
            
            if campos_faltantes:
                return False, f"Campos requeridos faltantes: {', '.join(campos_faltantes)}"
        
        # Validar formato de vigencia si está presente
        if 'vigencia' in datos and datos['vigencia']:
            try:
                # Intentar parsear la fecha
                if isinstance(datos['vigencia'], str):
                    datetime.fromisoformat(datos['vigencia'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False, "Formato de vigencia inválido. Use formato ISO: YYYY-MM-DD"
        
        # Validar longitud mínima de campos de texto largos
        if 'CER' in datos and len(datos['CER']) < 10:
            return False, "El contenido del archivo CER es demasiado corto"
        
        if 'KEY' in datos and len(datos['KEY']) < 10:
            return False, "El contenido del archivo KEY es demasiado corto"
        
        # Certificado es opcional, ya que se genera automáticamente desde CER
        if 'Certificado' in datos and datos['Certificado'] and len(datos['Certificado']) < 10:
            return False, "El contenido del Certificado es demasiado corto"
        
        return True, ""
    
    def crear_certificado(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        # Crea un nuevo certificado PAC.

        try:
            # Validar datos
            valido, mensaje = self.validar_datos_certificado(datos, es_actualizacion=False)
            if not valido:
                raise ValueError(mensaje)
            
            # Verificar si ya existe un certificado con el mismo usuario PAC
            certificado_existente = self.db_manager.get_certificado_by_usuario(datos['usuarioPAC'])
            if certificado_existente:
                raise ValueError(f"Ya existe un certificado para el usuario PAC: {datos['usuarioPAC']}")
            
            # Decodificar CER/KEY si vienen en base64 y almacenar bytes
            cer_value = datos['CER']
            key_value = datos['KEY']
            if isinstance(cer_value, str):
                try:
                    cer_bytes = base64.b64decode(cer_value)
                except Exception:
                    raise ValueError("El campo CER no contiene base64 válido")
            else:
                cer_bytes = cer_value

            if isinstance(key_value, str):
                try:
                    key_bytes = base64.b64decode(key_value)
                except Exception:
                    raise ValueError("El campo KEY no contiene base64 válido")
            else:
                key_bytes = key_value

            # Extraer noCertificado y vigencia del archivo .cer si no se proporcionaron
            try:
                info_certificado = self.extraer_info_certificado(cer_bytes)
                
                # Usar valores extraídos si no se proporcionaron manualmente
                if not datos.get('noCertificado'):
                    datos['noCertificado'] = info_certificado['noCertificado']
                    logger.info(f"noCertificado extraído automáticamente: {datos['noCertificado']}")
                else:
                    logger.info(f"Usando noCertificado proporcionado manualmente: {datos['noCertificado']}")
                
                if not datos.get('vigencia'):
                    datos['vigencia'] = info_certificado['vigencia']
                    logger.info(f"Vigencia extraída automáticamente: {datos['vigencia']}")
                else:
                    logger.info(f"Usando vigencia proporcionada manualmente: {datos['vigencia']}")
                    
            except ValueError as e:
                # Si falla la extracción y no se proporcionaron los valores, fallar
                if not datos.get('noCertificado') or not datos.get('vigencia'):
                    raise ValueError(f"No se pudo extraer información del certificado y no se proporcionaron manualmente: {str(e)}")
                logger.warning(f"No se pudo extraer información del certificado, usando valores manuales: {str(e)}")

            # Si no viene Certificado, usar el mismo CER (es el mismo contenido en base64)
            certificado_texto = datos.get('Certificado', datos['CER'])

            # Insertar certificado (CER/KEY como bytes)
            cert_id = self.db_manager.insert_certificado(
                usuarioPAC=datos['usuarioPAC'],
                contrasenaPAC=datos['contrasenaPAC'],
                nombreEmpresa=datos.get('nombreEmpresa', ''),
                CER=cer_bytes,
                KEY=key_bytes,
                vigencia=datos['vigencia'],
                noCertificado=datos['noCertificado'],
                Certificado=certificado_texto,
                correo=datos.get('correo', ''),
                telefono=datos.get('telefono', ''),
                pwdCER=datos['pwdCER'],  # Requerido
                claveUsuario=datos.get('claveUsuario')  # Nueva: clave única
            )
            
            logger.info(f"Certificado creado exitosamente con ID: {cert_id}")
            
            return {
                "success": True,
                "id": cert_id,
                "message": "Certificado creado exitosamente",
                "usuarioPAC": datos['usuarioPAC'],
                "noCertificado": datos['noCertificado'],
                "vigencia": datos['vigencia']
            }
            
        except ValueError as e:
            logger.warning(f"Error de validación al crear certificado: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al crear certificado: {e}")
            raise RuntimeError(f"Error al crear certificado: {str(e)}")
    
    def actualizar_certificado(self, cert_id: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        # Actualiza un certificado existente.

        try:
            if not datos:
                raise ValueError("No hay datos para actualizar")
            
            # Validar datos (permite actualizaciones parciales)
            valido, mensaje = self.validar_datos_certificado(datos, es_actualizacion=True)
            if not valido:
                raise ValueError(mensaje)
            
            # Si CER/KEY vienen en base64, decodificarlas a bytes antes de actualizar
            datos_to_update = datos.copy()
            
            # Eliminar campos que no se deben actualizar directamente
            datos_to_update.pop('id', None)
            datos_to_update.pop('activo', None)
            datos_to_update.pop('created_at', None)
            datos_to_update.pop('updated_at', None)
            
            if 'CER' in datos_to_update and isinstance(datos_to_update['CER'], str):
                try:
                    datos_to_update['CER'] = base64.b64decode(datos_to_update['CER'])
                except Exception:
                    raise ValueError("El campo CER no contiene base64 válido")
            if 'KEY' in datos_to_update and isinstance(datos_to_update['KEY'], str):
                try:
                    datos_to_update['KEY'] = base64.b64decode(datos_to_update['KEY'])
                except Exception:
                    raise ValueError("El campo KEY no contiene base64 válido")

            # Actualizar certificado
            success = self.db_manager.update_certificado(cert_id, **datos_to_update)
            
            if not success:
                raise ValueError(f"Certificado con ID {cert_id} no encontrado")
            
            logger.info(f"Certificado ID {cert_id} actualizado exitosamente")
            
            return {
                "success": True,
                "message": "Certificado actualizado exitosamente",
                "id": cert_id
            }
            
        except ValueError as e:
            logger.warning(f"Error de validación al actualizar certificado: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al actualizar certificado: {e}")
            raise RuntimeError(f"Error al actualizar certificado: {str(e)}")
    
    def eliminar_certificado(self, cert_id: int) -> Dict[str, Any]:
        """
        Desactiva un certificado (soft delete).
        El certificado se marca como inactivo pero no se elimina de la base de datos.
        
        Args:
            cert_id: ID del certificado a desactivar
            
        Returns:
            Diccionario con resultado de la desactivación
            
        Raises:
            ValueError: Si el certificado no existe o ya está inactivo
            RuntimeError: Si hay error al desactivar
        """
        try:
            success = self.db_manager.delete_certificado(cert_id)
            
            if not success:
                raise ValueError(f"Certificado con ID {cert_id} no encontrado o ya está inactivo")
            
            logger.info(f"Certificado ID {cert_id} desactivado exitosamente")
            
            return {
                "success": True,
                "message": "Certificado desactivado exitosamente",
                "id": cert_id
            }
            
        except ValueError as e:
            logger.warning(f"Error al desactivar certificado: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al desactivar certificado: {e}")
            raise RuntimeError(f"Error al desactivar certificado: {str(e)}")
    
    def obtener_certificados_proximos_vencer(self, dias: int = 30) -> List[Dict[str, Any]]:
        # Obtiene certificados que están próximos a vencer.

        # TODO: Implementar en DBManager.py si se necesita
        # Por ahora retorna lista vacía
        logger.info(f"Búsqueda de certificados próximos a vencer en {dias} días (no implementado)")
        return []
    
    def obtener_inactivos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los certificados inactivos.
        
        Returns:
            Lista de certificados inactivos
            
        Raises:
            RuntimeError: Si hay error al obtener los certificados
        """
        try:
            certificados = self.db_manager.get_certificados_inactivos()
            logger.info(f"Se obtuvieron {len(certificados)} certificados inactivos")
            return certificados
        except Exception as e:
            logger.error(f"Error obteniendo certificados inactivos: {e}")
            raise RuntimeError(f"Error al obtener certificados inactivos: {str(e)}")
    
    def reactivar_certificado(self, cert_id: int) -> Dict[str, Any]:
        """
        Reactiva un certificado inactivo.
        
        Args:
            cert_id: ID del certificado a reactivar
            
        Returns:
            Diccionario con resultado de la reactivación
            
        Raises:
            ValueError: Si el certificado no existe o ya está activo
            RuntimeError: Si hay error al reactivar
        """
        try:
            success = self.db_manager.reactivar_certificado(cert_id)
            
            if not success:
                raise ValueError(f"Certificado con ID {cert_id} no encontrado o ya está activo")
            
            logger.info(f"Certificado ID {cert_id} reactivado exitosamente")
            
            return {
                "success": True,
                "message": "Certificado reactivado exitosamente",
                "id": cert_id
            }
            
        except ValueError as e:
            logger.warning(f"Error al reactivar certificado: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al reactivar certificado: {e}")
            raise RuntimeError(f"Error al reactivar certificado: {str(e)}")
