from fastapi import FastAPI, HTTPException, status
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Añadir rutas al path PRIMERO
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_path)

from Business.Configuration.ConfiguracionLogin import ConfiguracionLogin, UsuarioLoginRequest
from Business.Configuration.ConfiguracionRegistro import ConfiguracionRegistro, UsuarioRegistroRequest
from Business.Configuration.ConfiguracionCertificados import ConfiguracionCertificados
from DB.DBManager import DBManager

app = FastAPI(
    title="DocuSeal Admin API",
    version="1.0.0",
    description="API administrativa para gestión de usuarios y certificados",
    root_path="/admin/api"  # Configuración para sub-aplicación montada en /admin/api
)

# Configurar CORS para el frontend administrativo
# Nota: Si se monta en la app principal, el CORS se maneja globalmente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
db_manager = DBManager()
login_service = ConfiguracionLogin(db_manager)
registro_service = ConfiguracionRegistro(db_manager)
certificados_service = ConfiguracionCertificados(db_manager)

# ==================== ENDPOINTS DE HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Endpoint de health check para verificar que el servidor está funcionando"""
    return {"status": "ok", "message": "DocuSeal Admin API is running"}

@app.get("/")
async def root():
    """
    Endpoint raíz - Retorna información básica de la API
    El frontend de React se ejecuta independientemente en el puerto 3000
    """
    return {
        "message": "DocuSeal Admin API",
        "version": "1.0.0",
        "frontend": "http://localhost:3000",
        "docs": "/docs"
    }

# ==================== ENDPOINTS DE AUTENTICACIÓN ====================

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_usuario(usuario: UsuarioRegistroRequest):
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        usuario: Datos del usuario a registrar
    
    Returns:
        Confirmación del registro exitoso
    """
    try:
        resultado = registro_service.registrar_usuario(usuario)
        return resultado
    except ValueError as e:
        # Errores de validación (contraseñas no coinciden, email duplicado, etc.)
        status_code = status.HTTP_409_CONFLICT if "ya está registrado" in str(e) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))
    except RuntimeError as e:
        # Errores del servidor
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        # Errores inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al registrar usuario: {str(e)}"
        )

@app.post("/login")
async def login_usuario(credenciales: UsuarioLoginRequest):
    """
    Autentica un usuario en el sistema.
    
    Args:
        credenciales: Email y contraseña del usuario
    
    Returns:
        Token de autenticación y datos del usuario
    """
    try:
        resultado = login_service.autenticar_usuario(credenciales)
        return resultado
    except ValueError as e:
        # Credenciales inválidas
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except RuntimeError as e:
        # Errores del servidor
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        # Errores inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado en el login: {str(e)}"
        )

# ==================== ENDPOINTS DE CERTIFICADOS ====================

@app.get("/v1/certificados/")
async def get_all_certificados():
    """
    Obtiene todos los certificados almacenados.
    
    Returns:
        Lista de certificados
    """
    try:
        return certificados_service.obtener_todos()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al obtener certificados: {str(e)}"
        )

@app.get("/v1/certificados/usuario/{usuario_pac}")
async def get_certificado_by_usuario(usuario_pac: str):
    """
    Obtiene un certificado por nombre de usuario PAC.
    
    Args:
        usuario_pac: Nombre de usuario del PAC
    
    Returns:
        Datos del certificado encontrado
    """
    try:
        certificado = certificados_service.obtener_por_usuario(usuario_pac)
        if not certificado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado no encontrado")
        return certificado
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al obtener certificado: {str(e)}"
        )

@app.get("/v1/certificados/numero/{no_certificado}")
async def get_certificado_by_numero(no_certificado: str):
    """
    Obtiene un certificado por número de certificado.
    
    Args:
        no_certificado: Número del certificado
    
    Returns:
        Datos del certificado encontrado
    """
    try:
        certificado = certificados_service.obtener_por_numero(no_certificado)
        if not certificado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado no encontrado")
        return certificado
    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al obtener certificado: {str(e)}"
        )

@app.post("/v1/certificados/", status_code=status.HTTP_201_CREATED)
async def create_certificado(certificado: dict = Body(...)):
    """
    Crea un nuevo certificado en el sistema.
    
    Args:
        certificado: Datos del certificado a crear
    
    Returns:
        Confirmación de creación con ID del certificado
    """
    try:
        return certificados_service.crear_certificado(certificado)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear certificado: {str(e)}"
        )

@app.put("/v1/certificados/{cert_id}")
async def update_certificado(cert_id: int, certificado: dict = Body(...)):
    """
    Actualiza un certificado existente.
    
    Args:
        cert_id: ID del certificado a actualizar
        certificado: Nuevos datos del certificado
    
    Returns:
        Confirmación de actualización
    """
    try:
        return certificados_service.actualizar_certificado(cert_id, certificado)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "no encontrado" in str(e) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al actualizar certificado: {str(e)}"
        )

@app.delete("/v1/certificados/{cert_id}")
async def delete_certificado(cert_id: int):
    """
    Desactiva un certificado del sistema (soft delete).
    El certificado se marca como inactivo pero no se elimina de la base de datos.
    
    Args:
        cert_id: ID del certificado a desactivar
    
    Returns:
        Confirmación de desactivación
    """
    try:
        return certificados_service.eliminar_certificado(cert_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al desactivar certificado: {str(e)}"
        )

@app.get("/v1/certificados/inactivos")
async def get_certificados_inactivos():
    """
    Obtiene todos los certificados inactivos.
    
    Returns:
        Lista de certificados inactivos
    """
    try:
        return certificados_service.obtener_inactivos()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al obtener certificados inactivos: {str(e)}"
        )

@app.patch("/v1/certificados/{cert_id}/reactivar")
async def reactivar_certificado(cert_id: int):
    """
    Reactiva un certificado inactivo.
    
    Args:
        cert_id: ID del certificado a reactivar
    
    Returns:
        Confirmación de reactivación
    """
    try:
        return certificados_service.reactivar_certificado(cert_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al reactivar certificado: {str(e)}"
        )

