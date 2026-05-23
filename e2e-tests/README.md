# Nayá API - E2E Test Suite

## 📋 Tabla de Contenidos
- [Integrantes del equipo](#integrantes-del-equipo)
- [Herramienta utilizada](#herramienta-utilizada)
- [Instrucciones de instalación y ejecución](#instrucciones-de-instalación-y-ejecución)
- [Descripción de los 6 flujos automatizados](#descripción-de-los-6-flujos-automatizados)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Datos de prueba](#datos-de-prueba)
- [Evidencia de ejecución](#evidencia-de-ejecución)
- [Mejoras futuras](#mejoras-futuras)

---

## 👥 Integrantes del equipo

- [Agrega aquí los nombres de los integrantes]
- Desarrollador: GitHub Copilot

---

## 🛠️ Herramienta utilizada

### Playwright (API Testing)

Se seleccionó **Playwright** como herramienta de automatización por las siguientes razones:

1. **Especialización en API Testing**: Aunque Playwright es conocido por testing de UI, su `APIRequestContext` es excelente para pruebas de API.
2. **Cross-browser support**: Permite validar con múltiples navegadores si se necesita.
3. **Fixtures y reutilización**: Sistema de fixtures poderoso para código limpio y mantenible.
4. **Reportes detallados**: Genera reportes HTML automáticamente.
5. **Mantenimiento activo**: Comunidad grande y actualizaciones constantes.
6. **Integración con CI/CD**: Fácil de integrar en pipelines.
7. **Validaciones robustas**: Sistema de assertions muy completo.

---

## 📦 Instrucciones de instalación y ejecución

### Requisitos previos
- **Node.js** 16+ (https://nodejs.org/)
- **Nayá API** corriendo en `http://localhost:8000`
- **npm** o **yarn**

### Instalación

1. Navega a la carpeta de tests:
   ```bash
   cd e2e-tests
   ```

2. Instala las dependencias:
   ```bash
   npm install
   ```

3. Instala los navegadores de Playwright:
   ```bash
   npx playwright install
   ```

### Ejecución

**Ejecutar todas las pruebas:**
```bash
npm test
```

**Ejecutar en modo headless con reporte:**
```bash
npm test
npm run test:report
```

**Ejecutar en modo debug:**
```bash
npm run test:debug
```

**Ejecutar en modo headed (ver ejecución en tiempo real):**
```bash
npm run test:headed
```

**Ejecutar en modo UI interactivo:**
```bash
npm run test:ui
```

**Ejecutar pruebas específicas:**
```bash
npx playwright test tests/auth.spec.ts
```

### Configuración

Edita el archivo `test-data.json` con tus datos de prueba:
```json
{
  "api": {
    "baseURL": "http://localhost:8000",
    "timeout": 30000
  },
  "patient": {
    "email": "patient.test@naya.dev",
    "password": "TestPassword123!",
    "confirmPassword": "TestPassword123!",
    "name": "TestPatient",
    "newPassword": "NewPass123!@",
    "newConfirmPassword": "NewPass123!@"
  },
  ...
}
```

---

## 🎯 Descripción de los 6 flujos automatizados

### FLOW 1: Registro de paciente y verificación de email

**Descripción**: Valida que un nuevo paciente pueda registrarse en la plataforma y recibir verificación por email.

**Pasos**:
1. Enviar POST a `/api/v1/patients` con datos válidos (nombre, email, contraseña)
2. Validar respuesta HTTP 201 (Created)
3. Validar estructura de respuesta (status, statusMessage, data)
4. Validar datos del paciente creado
5. Enviar POST a `/api/v1/auth/verification-code` con código de verificación
6. Validar respuesta de verificación

**Endpoints**: 
- `POST /api/v1/patients`
- `POST /api/v1/auth/verification-code`

**Validaciones**:
- Status code 201 (Created)
- Respuesta contiene `patient_id`, `email`, `name`
- `is_verified` inicia en `false`
- Código de verificación es aceptado

---

### FLOW 2: Login y obtención de JWT

**Descripción**: Valida el flujo de autenticación y obtención de tokens JWT para acceso a endpoints protegidos.

**Pasos**:
1. Enviar POST a `/api/v1/auth/login` con email y contraseña
2. Validar respuesta HTTP 200 (OK)
3. Extraer `access_token` y `refresh_token`
4. Validar que el token es válido usando un endpoint protegido (`/api/v1/auth/daily`)

**Endpoints**:
- `POST /api/v1/auth/login` (form-urlencoded)
- `GET /api/v1/auth/daily` (requiere Authorization header)

**Validaciones**:
- Status code 200
- Response contiene `access_token`, `refresh_token`, `user_type`
- `user_type` es "PATIENT"
- Token puede ser usado en endpoints protegidos

---

### FLOW 3: Solicitud de código de reseteo de contraseña

**Descripción**: Valida que un usuario pueda solicitar un código para resetear su contraseña.

**Pasos**:
1. Enviar POST a `/api/v1/auth/password-change-request` con email
2. Validar respuesta HTTP 200/204 (Success / No Content)
3. Validar que se envió email con código

**Endpoints**:
- `POST /api/v1/auth/password-change-request`

**Validaciones**:
- Status code 200 o 204
- Email válido es requerido
- Usuario debe existir

---

### FLOW 4: Validación de código de reseteo de contraseña

**Descripción**: Valida que el código recibido por email es correcto para el reseteo de contraseña.

**Pasos**:
1. Enviar POST a `/api/v1/auth/verification-code-password-reset` con código
2. Validar respuesta (puede ser válida o inválida)
3. Si es válido, código marca como usado

**Endpoints**:
- `POST /api/v1/auth/verification-code-password-reset`

**Validaciones**:
- Status code 200/204 si código es válido
- Status code 400 si código es inválido o ya usado
- Código solo puede usarse una vez

---

### FLOW 5: Reseteo de contraseña

**Descripción**: Valida que un usuario puede cambiar su contraseña usando el código de verificación.

**Pasos**:
1. Solicitar código de reseteo (FLOW 3)
2. Validar código (FLOW 4)
3. Enviar PUT a `/api/v1/auth/password-reset` con email, nueva contraseña y confirmación
4. Validar respuesta HTTP 200/204
5. Validar que puede hacer login con la nueva contraseña

**Endpoints**:
- `PUT /api/v1/auth/password-reset`

**Validaciones**:
- Status code 200/204 (exitoso) o 400 (error)
- Nueva contraseña debe cumplir validaciones (8-20 chars, mayús, minús, números, especiales)
- Las contraseñas deben coincidir
- Las contraseñas se hashen correctamente en base de datos

---

### FLOW 6: Conectar con terapeuta + Seleccionar perfil + Obtener consejo diario

**Descripción**: Valida el flujo completo de un paciente conectando con su terapeuta, seleccionando su avatar (animal), y accediendo a contenido protegido.

**Pasos**:
1. Hacer login (FLOW 2) para obtener JWT
2. Enviar POST a `/api/v1/auth/connect-patient-with-therapist` con código de conexión
3. Validar respuesta HTTP 200/204
4. Enviar POST a `/api/v1/auth/select-profile` con `user_id` e `id_animal`
5. Validar respuesta HTTP 200/204
6. Enviar GET a `/api/v1/auth/daily` para obtener consejo diario (endpoint protegido)
7. Validar respuesta HTTP 200 si usuario está verificado

**Endpoints**:
- `POST /api/v1/auth/connect-patient-with-therapist`
- `POST /api/v1/auth/select-profile`
- `GET /api/v1/auth/daily`

**Validaciones**:
- Requiere autenticación (JWT en Authorization header)
- Código de terapeuta debe ser válido
- Animal ID debe existir
- Respuesta de consejo contiene `id`, `title`, `description`
- Endpoint protegido retorna 401 sin token

---

## 📁 Estructura del proyecto

```
e2e-tests/
├── tests/
│   ├── auth.spec.ts           # Suite de pruebas principal
│   ├── fixtures.ts             # Configuración de fixtures
│   └── api.helper.ts           # Utilidades para llamadas API
├── test-data.json              # Datos de prueba
├── playwright.config.ts         # Configuración de Playwright
├── package.json                # Dependencias y scripts
└── README.md                   # Este archivo
```

### Componentes principales

**auth.spec.ts**:
- 12+ casos de prueba
- 6 flujos principales + validaciones de errores
- Pruebas de edge cases

**fixtures.ts**:
- Configuración de fixtures Playwright
- Carga de datos de prueba
- Inicialización de contexto API

**api.helper.ts**:
- Clase `ApiHelper` para abstraer llamadas HTTP
- Métodos helper para GET, POST, PUT
- Tipos TypeScript para responses

---

## 🔧 Datos de prueba

### Configuración mínima requerida

1. **Email de prueba**: Debe ser único y válido
2. **Contraseña**: Debe cumplir regex: `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$`
   - Ejemplo válido: `TestPassword123!`
   - Al menos: minúscula, mayúscula, número, carácter especial (@$!%*?&)
3. **Nombre**: 4-20 caracteres, solo letras
4. **Código de verificación**: Obtener de logs de email o base de datos
5. **Código de terapeuta**: Obtener del usuario terapeuta
6. **Animal ID**: UUID válido del animal a asociar

### Ejemplo de test-data.json

```json
{
  "api": {
    "baseURL": "http://localhost:8000",
    "timeout": 30000
  },
  "patient": {
    "email": "patient.test@naya.dev",
    "password": "TestPassword123!",
    "confirmPassword": "TestPassword123!",
    "name": "TestPatient",
    "newPassword": "NewPass123!@",
    "newConfirmPassword": "NewPass123!@"
  },
  "verification": {
    "code": "123456",
    "passwordResetCode": "654321"
  },
  "therapist": {
    "connectionCode": "THERAPIST001"
  },
  "profile": {
    "animalId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

## 📊 Evidencia de ejecución

### Ejecutar pruebas y generar reportes

```bash
npm test
npm run test:report
```

### Archivos generados

- `test-results/results.json` - Resultados en formato JSON
- `test-results/junit.xml` - Resultados en formato JUnit
- `playwright-report/` - Reporte HTML interactivo

### Ejemplo de salida esperada

```
running 12 tests

✓ FLOW 1.1: Register new patient with valid data (1500ms)
✓ FLOW 1.2: Validate verification code for email (800ms)
✓ FLOW 2.1: Login with valid credentials returns JWT (1200ms)
✓ FLOW 2.2: Verify JWT token is valid for protected endpoints (900ms)
✓ FLOW 3.1: Request password reset verification code (1100ms)
✓ FLOW 4.1: Validate password reset verification code (950ms)
✓ FLOW 5.1: Reset password with new password (1300ms)
✓ FLOW 6.1: Connect patient with therapist (1400ms)
✓ FLOW 6.2: Select profile picture with animal ID (850ms)
✓ FLOW 6.3: Get daily advice (protected endpoint) (900ms)
✓ ERROR: Login with invalid email returns 401 (800ms)
✓ ERROR: Register with duplicate email returns 403 (1100ms)

12 passed (12.5s)
```

---

## 🔍 Validaciones y Assertions

Las pruebas incluyen validaciones de:

### ✅ Validaciones funcionales
- Códigos de estado HTTP correctos
- Estructura de respuesta correcta
- Datos retornados válidos
- Tokens JWT válidos
- Autenticación requerida en endpoints protegidos

### ✅ Validaciones de seguridad
- Contraseñas no se retornan en respuestas
- Tokens son validados en endpoints protegidos
- Acceso denegado sin autenticación
- Emails únicos por usuario

### ✅ Validaciones de negocio
- Usuarios no verificados no pueden acceder
- Códigos solo se usan una vez
- Contraseñas deben cumplir requisitos
- Datos de usuario correctos tras registro

---

## 🚀 Mejoras futuras

1. **Pruebas de carga**: Agregar pruebas con múltiples usuarios concurrentes
2. **Pruebas de seguridad**: Validar protecciones contra:
   - SQL Injection
   - XSS
   - CSRF
3. **Pruebas de performance**: Medir tiempos de respuesta
4. **Cobertura de más endpoints**: Probar resto del API
5. **Integración con CI/CD**: Ejecutar automáticamente en push
6. **Reportes visuales**: Agregar gráficos y dashboards
7. **Pruebas en paralelo**: Aumentar velocidad de ejecución
8. **Base de datos de prueba**: Fixtures con datos seeded
9. **Pruebas con múltiples roles**: Terapeuta, padre, admin
10. **Documentación OpenAPI**: Validar contra spec

---

## 📚 Referencias

- [Documentación de Playwright](https://playwright.dev/)
- [Playwright API Testing](https://playwright.dev/docs/api-testing)
- [Nayá API Endpoints](../README.md)

---

## 📞 Contacto y Soporte

Para preguntas o issues:
1. Revisar logs en `test-results/`
2. Ejecutar en modo debug: `npm run test:debug`
3. Consultar documentación de endpoints en `/api/v1/docs`

---

**Última actualización**: Mayo 2026
