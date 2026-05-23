# Guía detallada de ejecución de pruebas E2E

## 📋 Tabla de Contenidos
1. [Prerequisitos](#prerequisitos)
2. [Instalación rápida](#instalación-rápida)
3. [Configuración del ambiente](#configuración-del-ambiente)
4. [Ejecución básica](#ejecución-básica)
5. [Ejecución avanzada](#ejecución-avanzada)
6. [Interpretación de resultados](#interpretación-de-resultados)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisitos

### Sistema requerido
- Windows 10+, macOS 10.13+, o Linux
- Node.js 16+
- npm 7+

### Verificar instalación

```bash
node --version      # Debe ser v16 o superior
npm --version       # Debe ser 7 o superior
```

### API corriendo
La Nayá API debe estar disponible en `http://localhost:8000`

Para iniciar desde el proyecto raíz:
```bash
# En Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Instalación rápida

### Opción 1: Script automático

**Windows:**
```powershell
cd e2e-tests
.\setup.bat
```

**macOS/Linux:**
```bash
cd e2e-tests
chmod +x setup.sh
./setup.sh
```

### Opción 2: Manual

```bash
cd e2e-tests
npm install
npx playwright install
```

---

## Configuración del ambiente

### 1. Editar datos de prueba

Modifica `test-data.json` con tus valores reales:

```json
{
  "api": {
    "baseURL": "http://localhost:8000",
    "timeout": 30000
  },
  "patient": {
    "email": "tu-email@test.com",
    "password": "TuPassword123!",
    "confirmPassword": "TuPassword123!",
    "name": "TuNombre",
    "newPassword": "NuevaPass123!",
    "newConfirmPassword": "NuevaPass123!"
  },
  "verification": {
    "code": "código-obtenido-del-email",
    "passwordResetCode": "código-obtenido-del-email"
  },
  "therapist": {
    "connectionCode": "código-del-terapeuta"
  },
  "profile": {
    "animalId": "uuid-del-animal"
  }
}
```

### 2. Variables de ambiente (opcional)

Crea un archivo `.env` en la carpeta `e2e-tests`:

```env
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30000
TEST_EMAIL=patient.test@example.com
TEST_PASSWORD=TestPassword123!
```

---

## Ejecución básica

### Ejecutar todas las pruebas

```bash
npm test
```

**Salida esperada:**
```
running 12 tests using 1 worker

✓ FLOW 1.1: Register new patient with valid data
✓ FLOW 1.2: Validate verification code for email
✓ FLOW 2.1: Login with valid credentials returns JWT
✓ FLOW 2.2: Verify JWT token is valid for protected endpoints
✓ FLOW 3.1: Request password reset verification code
✓ FLOW 4.1: Validate password reset verification code
✓ FLOW 5.1: Reset password with new password
✓ FLOW 6.1: Connect patient with therapist using connection code
✓ FLOW 6.2: Select profile picture with animal ID
✓ FLOW 6.3: Get daily advice (protected endpoint)
✓ ERROR: Login with invalid email returns 401
✓ ERROR: Register with duplicate email returns 403

12 passed (12.5s)
```

### Ver reporte HTML

```bash
npm run test:report
```

Abre automáticamente el reporte en el navegador con:
- Screenshots de cada test
- Videos de ejecución
- Tiempos de respuesta
- Trazas de ejecución

---

## Ejecución avanzada

### Modo debug (paso a paso)

```bash
npm run test:debug
```

Abre Playwright Inspector donde puedes:
- Pausar ejecución
- Ver elementos de la página
- Ejecutar comandos en consola

### Modo headed (ver ejecución en tiempo real)

```bash
npm run test:headed
```

Abre el navegador y muestra cada paso de la ejecución.

### Modo UI interactivo

```bash
npm run test:ui
```

Interfaz visual donde puedes:
- Ejecutar tests individuales
- Ver traces en tiempo real
- Inspeccionar elementos

### Ejecutar test específico

```bash
# Ejecutar solo FLOW 1
npx playwright test -g "FLOW 1"

# Ejecutar solo FLOW 2
npx playwright test -g "FLOW 2"

# Ejecutar solo pruebas de error
npx playwright test -g "ERROR"

# Ejecutar archivo específico
npx playwright test tests/auth.spec.ts
```

### Ejecutar con diferentes navegadores

```bash
# Configurar en playwright.config.ts para múltiples browsers
# Luego ejecutar:
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

### Ejecutar con reportes

```bash
# JSON report (para CI/CD)
npx playwright test --reporter=json

# JUnit report (para Jenkins)
npx playwright test --reporter=junit

# HTML report
npx playwright test --reporter=html
```

### Ejecutar en paralelo

```bash
# Con 4 workers (ver configuración)
npx playwright test --workers=4

# Sin paralelismo
npx playwright test --workers=1
```

---

## Interpretación de resultados

### Estados posibles

| Estado | Significado | Acción |
|--------|-------------|--------|
| ✓ | Test pasó | Sin acción |
| ✗ | Test falló | Ver logs |
| ⊙ | Test skip | Ver configuración |
| ⊗ | Test interrumpido | Revisar timeout |

### Logs

Encuentra logs detallados en:
- `test-results/results.json` - Datos completos en JSON
- `test-results/junit.xml` - Formato JUnit para CI
- `playwright-report/` - Reporte HTML interactivo

### Ver logs específicos

```bash
# Ver stdout de los tests
npx playwright test --reporter=verbose

# Ver trazas detalladas
npm run test:debug

# Guardar video de cada test
# (configurado en playwright.config.ts)
```

---

## Troubleshooting

### Error: "Connection refused" (Puerto 8000 no disponible)

```bash
# Verificar que la API está corriendo
curl http://localhost:8000/

# Si no funciona, iniciar la API
# En la raíz del proyecto:
uvicorn app.main:app --reload --port 8000
```

### Error: "Timeout waiting for response"

```bash
# Aumentar timeout en test-data.json
"timeout": 60000  # 60 segundos

# O ejecutar con timeout mayor
npx playwright test --timeout=60000
```

### Error: "Invalid verification code"

```
Causa: El código en test-data.json está expirado
Solución: 
1. Solicitar código nuevo en la API
2. Actualizar test-data.json en 2 minutos (tiempo de expiración)
```

### Error: "Duplicate email"

```
Causa: El email ya existe en la BD
Solución:
1. Usar email diferente en test-data.json
2. O limpiar BD de prueba
```

### Error: "npm: command not found"

```bash
# Node.js/npm no instalado
# Descargar e instalar desde https://nodejs.org/

# O usando package manager:
# Windows (Chocolatey):
choco install nodejs

# macOS (Homebrew):
brew install node

# Linux (apt):
sudo apt-get install nodejs npm
```

### Tests muy lento

```bash
# Verificar conexión de red
ping 8.8.8.8

# Ejecutar con menos workers
npx playwright test --workers=1

# Aumentar timeout
npx playwright test --timeout=60000

# Verificar recursos del sistema
# (CPU, RAM disponible)
```

### Error en TypeScript

```bash
# Reinstalar tipos
npm install --save-dev @types/node

# Limpiar y reinstalar
rm -rf node_modules package-lock.json
npm install

# Compilar TypeScript
npx tsc --noEmit
```

---

## Casos de uso comunes

### Antes de hacer push (verificación rápida)

```bash
npm test
```

### Para CI/CD (con reportes)

```bash
npm test -- --reporter=json --reporter=junit
```

### Para desarrollo (ver en tiempo real)

```bash
npm run test:headed
```

### Para debugging de test específico

```bash
npx playwright test -g "FLOW 1.1" --debug
```

### Para integración continua

```bash
# Con retry automático
npx playwright test --retries=2

# Generar reportes
npm test -- --reporter=html
npm run test:report
```

---

## Variables de entorno

Puedes usar variables de entorno para flexibilidad:

```bash
# En terminal
export API_BASE_URL=http://localhost:8000
export API_TIMEOUT=30000

# En Windows (cmd)
set API_BASE_URL=http://localhost:8000
set API_TIMEOUT=30000

# En Windows (PowerShell)
$env:API_BASE_URL="http://localhost:8000"
$env:API_TIMEOUT="30000"
```

Luego en `fixtures.ts`:

```typescript
const baseURL = process.env.API_BASE_URL || 'http://localhost:8000';
const timeout = parseInt(process.env.API_TIMEOUT || '30000');
```

---

## Próximos pasos

1. ✅ Configurar test-data.json
2. ✅ Ejecutar `npm install`
3. ✅ Ejecutar `npx playwright install`
4. ✅ Ejecutar `npm test`
5. ✅ Ver reporte: `npm run test:report`
6. ✅ Integrar en CI/CD
7. ✅ Ejecutar regularmente

---

**Para más información**: Ver README.md
