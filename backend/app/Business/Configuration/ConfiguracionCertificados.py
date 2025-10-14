"""
Módulo de configuración y lógica para la gestión de certificados PAC.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfiguracionCertificados:
    """Clase para manejar la lógica de gestión de certificados PAC."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
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
    
    def validar_datos_certificado(self, datos: Dict[str, Any], es_actualizacion: bool = False) -> tuple[bool, str]:
        # Valida los datos de un certificado antes de crear o actualizar.
        
        if not es_actualizacion:
            # Validar campos requeridos solo en creación
            # Certificado NO es requerido, se genera automáticamente desde CER
            campos_requeridos = ['usuarioPAC', 'contrasenaPAC', 'noCertificado', 'vigencia', 'CER', 'KEY', 'pwdCER']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or datos[campo] is None]
            
            if campos_faltantes:
                return False, f"Campos requeridos faltantes: {', '.join(campos_faltantes)}"
        
        # Validar formato de vigencia si está presente
        if 'vigencia' in datos:
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
                pwdCER=datos['pwdCER']  # Requerido
            )
            
            logger.info(f"Certificado creado exitosamente con ID: {cert_id}")
            
            return {
                "success": True,
                "id": cert_id,
                "message": "Certificado creado exitosamente",
                "usuarioPAC": datos['usuarioPAC']
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
