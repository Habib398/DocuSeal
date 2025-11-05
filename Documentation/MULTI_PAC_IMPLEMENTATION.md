# Implementación de Soporte Multi-PAC

## Estado Actual

DocuSeal actualmente sólo soporta **Comercio Digital** como proveedor PAC. El código está hardcodeado en los siguientes archivos:

- `backend/app/Business/Timbrado.py` (línea 28)
- `backend/app/Business/Cancelacion.py` (línea 124)

## PACs Disponibles en satcfdi

La librería `satcfdi` versión 4.8.1 incluye soporte para:
- comerciodigital (actual)
- diverza
- finkok
- mysuite
- prodigia
- sat
- swsapien

## Cambios Necesarios

### 1. Base de Datos
Agregar campo `tipoPAC` a la tabla `certificados_pac`:

```sql
ALTER TABLE certificados_pac 
ADD COLUMN tipoPAC VARCHAR(50) DEFAULT 'comerciodigital' NOT NULL;
```

### 2. DBManager
Actualizar `backend/app/DB/DBManager.py`:

- Método `_normalize_cert_keys`: agregar `'tipoPAC': cert_dict.get('tipopac')`
- Método `insert_certificado`: agregar parámetro `tipoPAC='comerciodigital'`
- Actualizar todas las consultas SQL que insertan certificados

### 3. Factory Pattern para PACs
Crear archivo `backend/app/Business/PACFactory.py`:

```python
from satcfdi.pacs import Environment
from satcfdi.pacs.comerciodigital import ComercioDigital
from satcfdi.pacs.finkok import Finkok
from satcfdi.pacs.diverza import Diverza
from satcfdi.pacs.mysuite import MySuite
from satcfdi.pacs.prodigia import Prodigia
from satcfdi.pacs.swsapien import SWSapien

class PACFactory:
    """Factory para crear instancias de diferentes PACs"""
    
    PAC_CLASSES = {
        'comerciodigital': ComercioDigital,
        'finkok': Finkok,
        'diverza': Diverza,
        'mysuite': MySuite,
        'prodigia': Prodigia,
        'swsapien': SWSapien,
    }
    
    @classmethod
    def crear_pac(cls, tipo_pac: str, usuario: str, password: str, pruebas: bool = True):
        """
        Crea una instancia del PAC especificado.
        
        Args:
            tipo_pac: Tipo de PAC (comerciodigital, finkok, etc.)
            usuario: Usuario del PAC
            password: Contraseña del PAC
            pruebas: Si es ambiente de pruebas
            
        Returns:
            Instancia del PAC correspondiente
            
        Raises:
            ValueError: Si el tipo de PAC no está soportado
        """
        tipo_pac = tipo_pac.lower()
        
        if tipo_pac not in cls.PAC_CLASSES:
            raise ValueError(
                f"PAC '{tipo_pac}' no soportado. "
                f"Opciones: {', '.join(cls.PAC_CLASSES.keys())}"
            )
        
        pac_class = cls.PAC_CLASSES[tipo_pac]
        env = Environment.TEST if pruebas else Environment.PRODUCTION
        
        return pac_class(user=usuario, password=password, environment=env)
    
    @classmethod
    def tipos_disponibles(cls):
        """Retorna lista de tipos de PAC soportados"""
        return list(cls.PAC_CLASSES.keys())
```

### 4. Modificar Timbrado.py
Reemplazar líneas 27-28:

```python
# Antes:
# Se desea implementar varios pac (Implementar a futuro)
pac = ComercioDigital(user=usuario_pac, password=contrasena_pac, environment=env)

# Después:
from .PACFactory import PACFactory

pac = PACFactory.crear_pac(tipo_pac, usuario_pac, contrasena_pac, pruebas)
```

Agregar parámetro `tipo_pac` a los métodos:
- `timbrar_cfdi(cls, xml, usuario_pac, contrasena_pac, pruebas, tipo_pac='comerciodigital')`
- `_procesar_timbrado(cls, xml, usuario_pac, contrasena_pac, pruebas, tipo_pac='comerciodigital')`

### 5. Modificar Cancelacion.py
Reemplazar línea 124:

```python
# Antes:
pac = ComercioDigital(
    user=usuario_pac,
    password=password_pac,
    environment=environment
)

# Después:
from Business.PACFactory import PACFactory

pac = PACFactory.crear_pac(
    tipo_pac=tipo_pac,
    usuario=usuario_pac,
    password=password_pac,
    pruebas=(environment == Environment.TEST)
)
```

Agregar parámetro `tipo_pac` al método `cancelar_uuid`.

### 6. Servicios (Service Layer)
Actualizar `backend/app/Business/Services/ServicioTimbrado.py`:

```python
# Obtener tipo de PAC desde el certificado
tipo_pac = certificado.get('tipoPAC', 'comerciodigital')

# Pasar tipo_pac al servicio de timbrado
resultado_timbrado = TimbradoService.timbrar_cfdi(
    xml_input, 
    usuario_pac, 
    contrasena_pac, 
    pruebas,
    tipo_pac=tipo_pac
)
```

Aplicar cambio similar en `ServicioCancelacion.py`.

### 7. API Admin
Modificar `backend/app/api_admin/main.py` endpoint de subir certificados:

- Agregar campo `tipoPAC` en el request body
- Validar que el tipo de PAC sea válido usando `PACFactory.tipos_disponibles()`
- Pasar `tipoPAC` al método `insert_certificado`

### 8. Frontend
Actualizar `Frontend/react-app/src/` componentes de certificados:

- Agregar selector dropdown con tipos de PAC disponibles
- Enviar `tipoPAC` en el request al subir certificados
- Mostrar tipo de PAC en la lista de certificados

## Notas Importantes
- Cada PAC puede tener diferentes tiempos de respuesta
- Los códigos de error varían entre PACs
- Las credenciales de prueba deben obtenerse de cada proveedor
- Algunos PACs pueden requerir configuración adicional (IPs autorizadas, certificados, etc.)
- Verificar límites de timbrado por PAC (algunos tienen restricciones diferentes)
```
