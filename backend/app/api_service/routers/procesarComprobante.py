from fastapi import APIRouter, Body, status
from typing import Dict, Any
from fastapi import APIRouter, Body, HTTPException
from Business.cfdi.ComprobanteFactory import ComprobanteFactory
from api_service import routers 

@routers.post("/procesar-comprobante", response_model=Dict[str, Any])
async def procesar_comprobante_endpoint(datos_json: Dict[str, Any]):
    try:
        # Llama al proceso principal
        resultado = ComprobanteFactory.procesar_comprobante(datos_json)
        
        # Si no es válido, lanza error HTTP con detalles
        if not resultado["valido"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "mensaje": "Errores de validación en el comprobante",
                    "errores": resultado["errores"],
                    "warnings": resultado["warnings"]
                }
            )
        
        # Retorna éxito con XML y warnings
        return {
            "mensaje": "Comprobante procesado exitosamente",
            "xml": resultado["xml"],
            "warnings": resultado["warnings"]
        }
    
    except ValueError as e:
        # Errores de tipo inválido (de ComprobanteFactory)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "errores": [{
                    "tipo": "error",
                    "codigo": "PROC001",
                    "mensaje": f"Tipo de comprobante inválido: {str(e)}"
                }]
            }
        )
    except NotImplementedError as e:
        # Tipo válido pero no implementado
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "errores": [{
                    "tipo": "error",
                    "codigo": "PROC002",
                    "mensaje": f"Tipo no implementado: {str(e)}"
                }]
            }
        )
    except Exception as e:
        # Errores inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "errores": [{
                    "tipo": "error",
                    "codigo": "PROC003",
                    "mensaje": f"Error interno: {str(e)}"
                }]
            }
        )
