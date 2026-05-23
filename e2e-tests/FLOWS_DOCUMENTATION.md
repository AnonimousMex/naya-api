# Mapeo de Flujos E2E a Casos de Uso del Sistema

## 🎯 Cobertura de Flujos

Esta suite de pruebas E2E cubre **6 flujos significativos** y **8+ casos de validación de errores** del sistema Nayá, validando funcionalidades críticas de la plataforma.

---

## Flujos Principales

### FLOW 1: Registro de Paciente y Verificación de Email

**Caso de uso del negocio**: Permitir que nuevos pacientes se registren en la plataforma y validen su identidad mediante email.

**Requisitos cubiertos**:
- ✅ Registro con datos válidos
- ✅ Validación de contraseña fuerte
- ✅ Email único por usuario
- ✅ Estado inicial de no verificado
- ✅ Envío de código por email
- ✅ Validación del código de verificación

**Pasos de prueba**:
```
POST /api/v1/patients
├─ name: string (4-20 chars, solo letras)
├─ email: string (único, max 40 chars)
├─ password: string (8-20 chars, validaciones fuertes)
├─ confirm_password: string (debe coincidir)
└─ Response: 201 Created
   ├─ patient_id: UUID
   ├─ email: string
   ├─ is_verified: false
   └─ created_at: timestamp

POST /api/v1/auth/verification-code
├─ code: string
└─ Response: 200/204 OK
   └─ user.is_verified: true
```

**Valor de negocio**: Asegurar que solo usuarios reales y verificados puedan acceder a la plataforma.

---

### FLOW 2: Login y Obtención de JWT

**Caso de uso del negocio**: Permitir que usuarios autenticados inicien sesión y obtengan tokens para acceder a endpoints protegidos.

**Requisitos cubiertos**:
- ✅ Autenticación con email/contraseña
- ✅ Generación de JWT válido
- ✅ Generación de refresh token
- ✅ Identificación del tipo de usuario (PATIENT)
- ✅ Acceso a endpoints protegidos con token

**Pasos de prueba**:
```
POST /api/v1/auth/login
├─ username: email
├─ password: string
└─ Response: 200 OK
   ├─ access_token: JWT
   ├─ refresh_token: JWT
   ├─ user_type: "PATIENT"
   └─ status: "Login success"

GET /api/v1/auth/daily (con Authorization: Bearer {token})
├─ Headers: Authorization: Bearer {access_token}
└─ Response: 200/403 OK
   ├─ id: UUID
   ├─ title: string
   └─ description: string
```

**Valor de negocio**: Asegurar autenticación segura y acceso controlado a recursos protegidos.

---

### FLOW 3: Solicitud de Código de Reseteo de Contraseña

**Caso de uso del negocio**: Permitir que usuarios olviden su contraseña y soliciten resetearla de manera segura.

**Requisitos cubiertos**:
- ✅ Solicitud por email válido
- ✅ Generación de código único
- ✅ Envío por email
- ✅ Código con expiración (2 minutos)
- ✅ Confirmación al usuario

**Pasos de prueba**:
```
POST /api/v1/auth/password-change-request
├─ email: string
└─ Response: 200/204 No Content
   └─ Email enviado con código
```

**Valor de negocio**: Recuperación segura de acceso sin comprometer cuentas.

---

### FLOW 4: Validación de Código de Reseteo de Contraseña

**Caso de uso del negocio**: Validar que el código recibido por email es correcto antes de permitir cambio de contraseña.

**Requisitos cubiertos**:
- ✅ Validación del código
- ✅ Verificación de expiración
- ✅ Uso único del código
- ✅ Mensajes de error claros

**Pasos de prueba**:
```
POST /api/v1/auth/verification-code-password-reset
├─ code: string
└─ Response: 200/204 OK (si es válido)
             400 Bad Request (si es inválido/expirado)
```

**Valor de negocio**: Asegurar que solo el usuario propietario del email pueda resetear la contraseña.

---

### FLOW 5: Reseteo de Contraseña

**Caso de uso del negocio**: Permitir que el usuario establezca una nueva contraseña después de validar el código.

**Requisitos cubiertos**:
- ✅ Cambio de contraseña seguro
- ✅ Validación de nueva contraseña
- ✅ Confirmación de coincidencia
- ✅ Hash de contraseña en BD
- ✅ Logout de otras sesiones

**Pasos de prueba**:
```
PUT /api/v1/auth/password-reset
├─ email: string
├─ password: string (nueva, con validaciones)
├─ confirm_password: string
└─ Response: 200/204 OK
   └─ Contraseña actualizada y hasheada
```

**Valor de negocio**: Permitir recuperación de acceso con seguridad mejorada.

---

### FLOW 6: Conexión con Terapeuta, Selección de Perfil y Acceso a Contenido Protegido

**Caso de uso del negocio**: Completar la configuración del perfil del paciente asignándole un terapeuta, seleccionando su avatar animal, y accediendo a contenido personalizado.

**Requisitos cubiertos**:
- ✅ Conexión paciente-terapeuta mediante código único
- ✅ Selección de animal/avatar del paciente
- ✅ Acceso a endpoints protegidos
- ✅ Contenido personalizado (consejo diario)
- ✅ Validación de autenticación en endpoints protegidos

**Pasos de prueba**:
```
1. Login (FLOW 2) → get JWT

2. POST /api/v1/auth/connect-patient-with-therapist
   ├─ code: string (código único del terapeuta)
   ├─ Authorization: Bearer {token}
   └─ Response: 200/204 OK
      └─ patient.is_connected: true

3. POST /api/v1/auth/select-profile
   ├─ user_id: UUID
   ├─ id_animal: UUID
   ├─ Authorization: Bearer {token}
   └─ Response: 200/204 OK
      └─ animal_id asignado al usuario

4. GET /api/v1/auth/daily (endpoint protegido)
   ├─ Authorization: Bearer {token}
   └─ Response: 200 OK (si está verificado)
               403 Forbidden (si no está verificado)
      ├─ id: UUID
      ├─ title: string
      ├─ description: string
      └─ createdAt: timestamp
```

**Valor de negocio**: Establecer la relación terapéutica y personalizar la experiencia del usuario.

---

## 📊 Casos de Validación de Errores

La suite incluye validaciones de error para asegurar manejo correcto de casos inválidos:

### Error Cases

| # | Escenario | Esperado | Validación |
|---|-----------|----------|-----------|
| 1 | Login con email inválido | 401 Unauthorized | Rechazo de credenciales |
| 2 | Login con contraseña incorrecta | 401 Unauthorized | Rechazo seguro sin info |
| 3 | Registro con email duplicado | 403 Forbidden | Prevención de duplicados |
| 4 | Acceso protegido sin token | 401 Unauthorized | Requerimiento de autenticación |
| 5 | Registro con contraseña débil | 422 Unprocessable Entity | Validación de formato |
| 6 | Registro con contraseñas no coincidentes | 403 Forbidden | Validación de coincidencia |

---

## 🔐 Validaciones de Seguridad

### Contraseña

Formato requerido: `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$`

Ejemplo válido: `TestPassword123!`

Requisitos:
- ✅ 8-20 caracteres
- ✅ Al menos una minúscula
- ✅ Al menos una mayúscula
- ✅ Al menos un número
- ✅ Al menos un carácter especial (@$!%*?&)

### Email

- ✅ Debe ser válido (RFC 5322)
- ✅ Máximo 40 caracteres
- ✅ Único por usuario

### Nombre

- ✅ 4-20 caracteres
- ✅ Solo letras

### JWT

- ✅ Generado usando HS256
- ✅ Contiene claims: sub (user_id), user_type, patient_or_therapist_id
- ✅ Validado en endpoints protegidos
- ✅ Rechazado si está expirado

---

## 📈 Cobertura de Endpoints

| Endpoint | Método | Status | Flujo |
|----------|--------|--------|-------|
| `/api/v1/patients` | POST | 201 | FLOW 1 |
| `/api/v1/auth/verification-code` | POST | 200/204 | FLOW 1 |
| `/api/v1/auth/login` | POST | 200 | FLOW 2 |
| `/api/v1/auth/daily` | GET | 200/403 | FLOW 2, 6 |
| `/api/v1/auth/password-change-request` | POST | 200/204 | FLOW 3 |
| `/api/v1/auth/verification-code-password-reset` | POST | 200/204 | FLOW 4 |
| `/api/v1/auth/password-reset` | PUT | 200/204 | FLOW 5 |
| `/api/v1/auth/connect-patient-with-therapist` | POST | 200/204 | FLOW 6 |
| `/api/v1/auth/select-profile` | POST | 200/204 | FLOW 6 |

---

## 🎓 Flujos de Usuario Reales

### Nuevo Usuario

```
1. Registro (FLOW 1)
   ↓
2. Verificar email (FLOW 1)
   ↓
3. Login (FLOW 2)
   ↓
4. Seleccionar avatar (FLOW 6)
   ↓
5. Conectar con terapeuta (FLOW 6)
   ↓
6. Acceder a consejo diario (FLOW 6)
```

### Usuario Olvidó Contraseña

```
1. Solicitar reset (FLOW 3)
   ↓
2. Verificar código (FLOW 4)
   ↓
3. Resetear contraseña (FLOW 5)
   ↓
4. Login con nueva contraseña (FLOW 2)
```

### Usuario Existente

```
1. Login (FLOW 2)
   ↓
2. Acceder a contenido (FLOW 6)
```

---

## 📋 Matriz de Combinaciones

Esta suite prueba las siguientes combinaciones:

```
Registro × Verificación × Login × Protegido
    ✓    ×      ✓       ×   ✓   = FLOW 1+2
    ✓    ×      ✓       ×   ✓   = FLOW 6
    -    ×      ✓       ×   ✓   = FLOW 5+2
    -    ×      ✓       ×   -   = FLOW 2
```

---

## 🔄 Secuencia Temporal

### Tiempos esperados por flujo

| Flujo | Operaciones | Tiempo típico |
|-------|------------|--------------|
| FLOW 1 | 2 requests | 2-3 segundos |
| FLOW 2 | 2 requests | 2-2.5 segundos |
| FLOW 3 | 1 request | 1-1.5 segundos |
| FLOW 4 | 1 request | 1-1.5 segundos |
| FLOW 5 | 1 request | 1-1.5 segundos |
| FLOW 6 | 3 requests | 3-4 segundos |
| **Total** | **12 requests** | **12-15 segundos** |

---

## 🎯 Métricas de Éxito

✅ **Todos los 6 flujos pasan exitosamente**
✅ **Todas las validaciones de error funcionan**
✅ **JWT se genera y valida correctamente**
✅ **Códigos de verificación se validan**
✅ **Autenticación se requiere en endpoints protegidos**
✅ **Status codes HTTP son correctos**
✅ **Estructura de respuesta es consistente**
✅ **Tiempos de respuesta < 2 segundos por endpoint**

---

## 📚 Relación con Requisitos

| Requisito | Cubierto por |
|-----------|-------------|
| Inicio y cierre de sesión | FLOW 2 |
| Registro o autenticación | FLOW 1, FLOW 2 |
| Navegación entre módulos | FLOW 2, FLOW 6 |
| Creación/edición de información | FLOW 1, FLOW 5, FLOW 6 |
| Validación de formularios | Todos los FLOWs |
| Validación de mensajes de error | Error Cases (6+ validaciones) |
| Procesos principales del sistema | FLOW 1-6 (ciclo completo) |

---

**Última actualización**: Mayo 2026
**Versión**: 1.0
