# Diagrama de Flujo - Sistema de Clave API

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FLUJO DE REGISTRO                            │
└─────────────────────────────────────────────────────────────────────┘

1. Usuario completa formulario de registro
   ├─ Nombre
   ├─ Email
   ├─ Contraseña
   └─ Confirmar Contraseña
          ↓
2. Usuario hace clic en "Registrar"
          ↓
3. Frontend genera UUID v4 (clave API)
   Ejemplo: "550e8400-e29b-41d4-a716-446655440000"
          ↓
4. Frontend envía a Backend (/api/register)
   {
     "name": "...",
     "email": "...",
     "password": "...",
     "confirm_password": "...",
     "api_key": "550e8400-e29b-41d4-a716-446655440000"
   }
          ↓
5. Backend procesa registro
   ├─ Valida datos
   ├─ Encripta contraseña
   ├─ Encripta api_key ⚠️ (IMPORTANTE)
   └─ Guarda en base de datos
          ↓
6. Backend responde
   {
     "success": true,
     "user": {
       "id": 123,
       "name": "...",
       "email": "..."
       // ⚠️ NO incluye api_key
     }
   }
          ↓
7. Frontend muestra ApiKeyModal
   ╔═══════════════════════════════════════════╗
   ║  🔑 ¡Importante! Tu Clave de Acceso      ║
   ║                                           ║
   ║  ⚠️ Esta clave solo se mostrará una vez  ║
   ║                                           ║
   ║  ┌─────────────────────────────────────┐ ║
   ║  │ 550e8400-e29b-41d4-a716-446655440000│ ║
   ║  └─────────────────────────────────────┘ ║
   ║                                           ║
   ║  [📋 Copiar Clave]                       ║
   ║                                           ║
   ║  Instrucciones:                          ║
   ║  • Guarda esta clave de forma segura    ║
   ║  • No la compartas con nadie             ║
   ║  • La necesitarás para acceder a datos  ║
   ║                                           ║
   ║  [Entendido, continuar al login]         ║
   ╚═══════════════════════════════════════════╝
          ↓
8. Usuario copia la clave y hace clic en "Entendido"
          ↓
9. Modal se cierra y redirige a LoginPage
          ↓
10. ✅ Usuario debe iniciar sesión normalmente


┌─────────────────────────────────────────────────────────────────────┐
│                          FLUJO DE LOGIN                              │
└─────────────────────────────────────────────────────────────────────┘

1. Usuario ingresa credenciales
   ├─ Email
   └─ Contraseña
          ↓
2. Frontend envía a Backend (/api/login)
   {
     "email": "...",
     "password": "..."
   }
          ↓
3. Backend valida credenciales
   ├─ Verifica email existe
   ├─ Verifica contraseña (hash)
   └─ Obtiene datos del usuario
          ↓
4. Backend responde
   {
     "success": true,
     "user": {
       "id": 123,
       "name": "...",
       "email": "..."
       // ⚠️ NO incluye api_key (por seguridad)
     }
   }
          ↓
5. Frontend guarda usuario en localStorage
          ↓
6. ✅ Usuario autenticado - Redirige a página de certificados


┌─────────────────────────────────────────────────────────────────────┐
│               FLUJO DE USO DE CLAVE (FUTURO)                         │
└─────────────────────────────────────────────────────────────────────┘

⚠️ Este flujo se implementará cuando el backend esté listo

1. Usuario autenticado quiere acceder a certificados
          ↓
2. Frontend necesita hacer request al servicio backend
   Endpoint: /api/v1/certificados
          ↓
3. Frontend incluye api_key en request
   Headers: {
     "X-API-Key": "550e8400-e29b-41d4-a716-446655440000"
   }
   // O como query parameter: ?api_key=...
          ↓
4. Backend de servicio valida api_key
   ├─ Busca en BD (comparando hash)
   ├─ Verifica que existe y es válida
   └─ Obtiene usuario asociado
          ↓
5. Si válida: Backend devuelve certificados del usuario
   Si inválida: Error 401 Unauthorized
          ↓
6. ✅ Frontend muestra certificados


┌─────────────────────────────────────────────────────────────────────┐
│            FLUJO DE RECUPERACIÓN (FUTURO - NO IMPLEMENTADO)         │
└─────────────────────────────────────────────────────────────────────┘

⚠️ Dejar preparado, no implementar aún

1. Usuario hace clic en "¿Olvidaste tu clave?"
          ↓
2. Frontend muestra modal de recuperación
          ↓
3. Usuario ingresa su email
          ↓
4. Frontend envía a Backend (/api/recover-api-key)
   { "email": "..." }
          ↓
5. Backend envía email con enlace de recuperación
          ↓
6. Usuario hace clic en enlace del email
          ↓
7. Backend valida token del enlace
          ↓
8. Backend genera nueva clave o muestra la existente
          ↓
9. ✅ Usuario guarda la nueva clave


┌─────────────────────────────────────────────────────────────────────┐
│                      SEGURIDAD DE LA CLAVE                           │
└─────────────────────────────────────────────────────────────────────┘

EN FRONTEND:
├─ Se genera con crypto.randomUUID() (criptográficamente seguro)
├─ Se muestra solo una vez (en modal después del registro)
├─ NO se guarda en localStorage permanentemente
├─ NO aparece en ninguna UI después del modal inicial
└─ Se limpia al hacer logout

EN BACKEND:
├─ Se guarda ENCRIPTADA en la base de datos
├─ NO se devuelve en respuestas de API
├─ Se usa para autenticar acceso a certificados
└─ Reemplaza el uso inseguro de "noCertificado"


┌─────────────────────────────────────────────────────────────────────┐
│                    ARCHIVOS MODIFICADOS                              │
└─────────────────────────────────────────────────────────────────────┘

NUEVOS:
✨ ApiKeyModal.tsx           - Modal para mostrar clave única

MODIFICADOS:
📝 RegistrarModal.tsx        - Genera UUID y muestra modal
📝 apiClient.ts              - Interfaces actualizadas + métodos auxiliares
📝 AuthContext.tsx           - Limpia clave en logout
📝 LoginForm.tsx             - Comentarios TODO para recuperación

DOCUMENTACIÓN:
📄 API_KEY_SYSTEM.md         - Sistema completo documentado
📄 FLOW_DIAGRAM.md           - Este archivo (diagramas de flujo)
```

## Ejemplo Práctico

### Caso de Uso: Nuevo Usuario "Juan"

1. **Registro**
   ```
   Juan completa formulario → Genera clave
   "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
   
   Backend guarda:
   - id: 5
   - name: "Juan Pérez"
   - email: "juan@example.com"
   - password_hash: "$2b$12$..." 
   - api_key_encrypted: "encrypted_string..."  ← ⚠️ Encriptada
   ```

2. **Modal mostrado a Juan**
   ```
   Tu clave: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   [Copiar] ← Juan hace clic y guarda en su gestor de contraseñas
   ```

3. **Login**
   ```
   Juan ingresa email y contraseña → Éxito
   Redirige a certificados
   ```

4. **Acceso a certificados (futuro)**
   ```
   Request: GET /api/v1/certificados
   Headers: X-API-Key: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   
   Backend valida → Devuelve certificados de Juan
   ```

## Ventajas del Sistema

✅ **Seguridad mejorada**: La clave es criptográficamente segura
✅ **Unicidad**: Cada usuario tiene su propia clave única
✅ **Privacidad**: La clave no se expone en la UI
✅ **Escalabilidad**: Fácil de integrar con servicios backend
✅ **Control**: El usuario es responsable de guardar su clave
✅ **Futuro**: Preparado para recuperación sin implementarla aún
