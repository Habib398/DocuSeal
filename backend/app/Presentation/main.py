from fastapi import FastAPI, HTTPException, status
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Añadir rutas al path PRIMERO
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_path)

from Business.SellarXML import SellarXML
from Business.Timbrado import TimbradoService
from Business.ConfiguracionLogin import ConfiguracionLogin, UsuarioLoginRequest
from Business.ConfiguracionRegistro import ConfiguracionRegistro, UsuarioRegistroRequest
from DB.DBManager import DBManager


app = FastAPI(title="DocuSeal API", version="1.0.0")

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
db_manager = DBManager()
login_service = ConfiguracionLogin(db_manager)
registro_service = ConfiguracionRegistro(db_manager)

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_usuario(usuario: UsuarioRegistroRequest):
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

@app.post("/api/login")
async def login_usuario(credenciales: UsuarioLoginRequest):
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

# Endpoint de health check
@app.get("/health")
async def health_check():
    """Endpoint para verificar que el servidor está funcionando."""
    return {"status": "ok", "message": "Server is running"}

# Endpoints para certificados
@app.get("/api/v1/certificados/")
async def get_all_certificados():
    """Obtiene todos los certificados."""
    try:
        certificados = db_manager.get_all_certificados()
        return certificados
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener certificados: {str(e)}"
        )

@app.get("/api/v1/certificados/usuario/{usuario_pac}")
async def get_certificado_by_usuario(usuario_pac: str):
    """Obtiene un certificado por usuario PAC."""
    try:
        certificado = db_manager.get_certificado_by_usuario(usuario_pac)
        if not certificado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado no encontrado")
        return certificado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener certificado: {str(e)}"
        )

@app.get("/api/v1/certificados/numero/{no_certificado}")
async def get_certificado_by_numero(no_certificado: str):
    """Obtiene un certificado por número de certificado."""
    try:
        certificado = db_manager.get_certificado_by_noCertificado(no_certificado)
        if not certificado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado no encontrado")
        return certificado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener certificado: {str(e)}"
        )

@app.post("/api/v1/certificados/", status_code=status.HTTP_201_CREATED)
async def create_certificado(certificado: dict = Body(...)):
    """Crea un nuevo certificado."""
    try:
        required_fields = ['usuarioPAC', 'contrasenaPAC', 'noCertificado', 'vigencia', 'CER', 'KEY', 'Certificado']
        for field in required_fields:
            if field not in certificado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo requerido faltante: {field}"
                )
        
        cert_id = db_manager.insert_certificado(
            usuarioPAC=certificado['usuarioPAC'],
            contrasenaPAC=certificado['contrasenaPAC'],
            nombreEmpresa=certificado.get('nombreEmpresa', ''),
            CER=certificado['CER'],
            KEY=certificado['KEY'],
            vigencia=certificado['vigencia'],
            noCertificado=certificado['noCertificado'],
            Certificado=certificado['Certificado']
        )
        
        return {"success": True, "id": cert_id, "message": "Certificado creado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear certificado: {str(e)}"
        )

@app.put("/api/v1/certificados/{cert_id}")
async def update_certificado(cert_id: int, certificado: dict = Body(...)):
    """Actualiza un certificado existente."""
    try:
        success = db_manager.update_certificado(cert_id, **certificado)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado no encontrado")
        return {"success": True, "message": "Certificado actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar certificado: {str(e)}"
        )

@app.delete("/api/v1/certificados/{cert_id}")
async def delete_certificado(cert_id: int):
    """Elimina un certificado."""
    try:
        success = db_manager.delete_certificado(cert_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado no encontrado")
        return {"success": True, "message": "Certificado eliminado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar certificado: {str(e)}"
        )

@app.post("/timbrar/")
async def timbrar_endpoint(
    xml: str = Body(..., embed=True),
    usuario_pac: str = Body(..., embed=True),
    contrasena_pac: str = Body(..., embed=True),
    pruebas: bool = Body(True, embed=True)
):
    return TimbradoService.timbrar_cfdi(xml, usuario_pac, contrasena_pac, pruebas)

@app.post("/sellar/")
async def sellar_endpoint(data: dict = Body(...)):
    return SellarXML.sellar_cfdi(data)

@app.post("/timbrarSellar/")
async def timbrar_sellar_endpoint(data: dict = Body(...)):
    # Sellado
    resultado_sellado = SellarXML.sellar_cfdi(data)
    if "error" in resultado_sellado:
        return resultado_sellado
    
    xml_sellado = resultado_sellado["xml_con_sello"]
    
    # Obtiene credenciales PAC
    usuario_pac = data.get("PAC", {}).get("usuario")
    contrasena_pac = data.get("PAC", {}).get("contrasena")
    pruebas = data.get("pruebas", True)
    
    if not usuario_pac or not contrasena_pac:
        return {"error": "Faltan credenciales PAC (objeto PAC incompleto o vacío)"}
    
    # Timbrado
    return TimbradoService.timbrar_cfdi(xml_sellado, usuario_pac, contrasena_pac, pruebas)