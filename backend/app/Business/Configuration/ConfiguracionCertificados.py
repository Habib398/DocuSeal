"""
Módulo de configuración y lógica para la gestión de certificados PAC.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

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
            campos_requeridos = ['usuarioPAC', 'contrasenaPAC', 'noCertificado', 'vigencia', 'CER', 'KEY', 'Certificado']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or not datos[campo]]
            
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
        
        if 'Certificado' in datos and len(datos['Certificado']) < 10:
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
            
            # Insertar certificado
            cert_id = self.db_manager.insert_certificado(
                usuarioPAC=datos['usuarioPAC'],
                contrasenaPAC=datos['contrasenaPAC'],
                nombreEmpresa=datos.get('nombreEmpresa', ''),
                CER=datos['CER'],
                KEY=datos['KEY'],
                vigencia=datos['vigencia'],
                noCertificado=datos['noCertificado'],
                Certificado=datos['Certificado'],
                correo=datos.get('correo', ''),
                telefono=datos.get('telefono', '')
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
            
            # Actualizar certificado
            success = self.db_manager.update_certificado(cert_id, **datos)
            
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
        Elimina un certificado.
        
        Args:
            cert_id: ID del certificado a eliminar
            
        Returns:
            Diccionario con resultado de la eliminación
            
        Raises:
            ValueError: Si el certificado no existe
            RuntimeError: Si hay error al eliminar
        """
        try:
            success = self.db_manager.delete_certificado(cert_id)
            
            if not success:
                raise ValueError(f"Certificado con ID {cert_id} no encontrado")
            
            logger.info(f"Certificado ID {cert_id} eliminado exitosamente")
            
            return {
                "success": True,
                "message": "Certificado eliminado exitosamente",
                "id": cert_id
            }
            
        except ValueError as e:
            logger.warning(f"Error al eliminar certificado: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al eliminar certificado: {e}")
            raise RuntimeError(f"Error al eliminar certificado: {str(e)}")
    
    def obtener_certificados_proximos_vencer(self, dias: int = 30) -> List[Dict[str, Any]]:
        # Obtiene certificados que están próximos a vencer.

        # TODO: Implementar en DBManager.py si se necesita
        # Por ahora retorna lista vacía
        logger.info(f"Búsqueda de certificados próximos a vencer en {dias} días (no implementado)")
        return []
