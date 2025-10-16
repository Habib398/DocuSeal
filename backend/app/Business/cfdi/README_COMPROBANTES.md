# Sistema de Comprobantes por Tipo

## Descripción

Se ha implementado un sistema de **Factory Pattern** para manejar diferentes tipos de comprobantes CFDI según el campo `TipoDeComprobante`. Cada tipo tiene su propia clase con validaciones y ajustes específicos según las reglas del SAT.

## Tipos de Comprobante Implementados

### ✅ Tipo "I" - Ingreso (`ComprobanteIngreso`)
**Archivo:** `backend/app/Business/cfdi/Comprobantes/Ingreso.py`

**Validaciones:**
- Total debe ser mayor a 0
- Debe tener MetodoPago (PPD, PUE, etc.)
- SubTotal - Descuento + ImpuestosTrasladados - ImpuestosRetenidos debe coincidir con Total
- Impuestos deben ser válidos si ObjetoImp lo requiere

**Ajustes automáticos:**
- Recalcula Total si hay discrepancias
- Asegura TipoDeComprobante = "I"

### ✅ Tipo "T" - Traslado (`ComprobanteTraslado`)
**Archivo:** `backend/app/Business/cfdi/Comprobantes/Traslados.py`

**Validaciones según reglas SAT:**
- Total debe ser 0.00 (CFDI40109)
- NO debe tener MetodoPago (CFDI40125)
- NO debe tener elemento cfdi:Impuestos a nivel comprobante (CFDI40201)
- SubTotal debe ser mayor a 0

**Ajustes automáticos:**
- Fuerza Total = "0.00"
- Elimina MetodoPago si existe
- Elimina cfdi:Impuestos a nivel comprobante si existe
- Asegura TipoDeComprobante = "T"

### 🔄 Tipos pendientes de implementación
- **"E" - Egreso**
- **"P" - Pago**
- **"N" - Nómina**

## Códigos de Error Personalizados

### Ingreso (ING)
- **ING001**: TipoDeComprobante debe ser 'I'
- **ING002**: Total debe ser mayor a 0
- **ING003**: Total no numérico
- **ING004**: MetodoPago requerido
- **ING005**: Total no coincide con cálculo
- **ING006**: Error al validar totales
- **ING007**: ObjetoImp indica impuestos pero no hay en concepto

### Traslado (TRA)
- **TRA001**: TipoDeComprobante debe ser 'T'
- **TRA002**: Total debe ser 0.00 (CFDI40109)
- **TRA003**: Total no numérico
- **TRA004**: MetodoPago debe omitirse (CFDI40125)
- **TRA005**: cfdi:Impuestos no debe existir (CFDI40201)
- **TRA006**: SubTotal debe ser > 0
- **TRA007**: SubTotal no numérico

## Testing

### Prueba manual con ejemplos

```powershell
# Probar tipo Ingreso
curl -X POST http://localhost:8001/api/service/sellar `
  -H "Content-Type: application/json" `
  -d @backend/app/ejemplos/endpoint_sellarJson_ejemplo.json

# Probar tipo Traslado
curl -X POST http://localhost:8001/api/service/sellar `
  -H "Content-Type: application/json" `
  -d @backend/app/ejemplos/endpoint_traslado_ejemplo.json
```

### Pruebas unitarias (recomendadas)

Crear `tests/test_comprobantes.py`:

```python
import pytest
from backend.app.Business.cfdi.ComprobanteFactory import ComprobanteFactory

def test_ingreso_valido():
    datos = {
        "cfdi:Comprobante": {
            "TipoDeComprobante": "I",
            "SubTotal": "100.00",
            "Total": "116.00",
            "MetodoPago": "PUE",
            ...
        }
    }
    resultado = ComprobanteFactory.procesar_comprobante(datos)
    assert resultado["valido"] == True
    assert resultado["xml"] is not None

def test_traslado_sin_metodo_pago():
    datos = {
        "cfdi:Comprobante": {
            "TipoDeComprobante": "T",
            "SubTotal": "1000.00",
            "Total": "0.00",
            ...
        }
    }
    resultado = ComprobanteFactory.procesar_comprobante(datos)
    assert resultado["valido"] == True
```

## Beneficios

✅ **Separación de responsabilidades**: cada tipo tiene su lógica aislada  
✅ **Validaciones específicas**: reglas del SAT por tipo  
✅ **Extensible**: agregar nuevos tipos es simple  
✅ **Mantenible**: cambios en un tipo no afectan otros  
✅ **Testeable**: tests unitarios por clase  
✅ **Compatible hacia atrás**: XML directo sigue funcionando  
✅ **Ajustes automáticos**: corrige datos según reglas SAT  

## Referencias

- Reglas SAT: `backend/app/Data/matriz_errores.txt`
- Validador base: `backend/app/Business/ValidadorCFDI.py`
- Generador XML: `backend/app/Business/cfdi/ConvertirJson.py`
- Ejemplos: `backend/app/ejemplos/`
