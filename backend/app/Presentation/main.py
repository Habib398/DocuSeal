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
from Business.ConfiguracionCertificados import ConfiguracionCertificados
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
certificados_service = ConfiguracionCertificados(db_manager)

# Endpoints de autenticación

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

# Endpoint de verificador de conexion (Copilot)
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server is running"}

# Endpoints para certificados
@app.get("/api/v1/certificados/")
async def get_all_certificados():
    try:
        return certificados_service.obtener_todos()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al obtener certificados: {str(e)}"
        )

@app.get("/api/v1/certificados/usuario/{usuario_pac}")
async def get_certificado_by_usuario(usuario_pac: str):
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

@app.get("/api/v1/certificados/numero/{no_certificado}")
async def get_certificado_by_numero(no_certificado: str):
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

@app.post("/api/v1/certificados/", status_code=status.HTTP_201_CREATED)
async def create_certificado(certificado: dict = Body(...)):
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

@app.put("/api/v1/certificados/{cert_id}")
async def update_certificado(cert_id: int, certificado: dict = Body(...)):
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

@app.delete("/api/v1/certificados/{cert_id}")
async def delete_certificado(cert_id: int):
    try:
        return certificados_service.eliminar_certificado(cert_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al eliminar certificado: {str(e)}"
        )

# Endpoints de proceso de timbrado y sellado
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
