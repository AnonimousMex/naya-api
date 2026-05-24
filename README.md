# 🩺 NAYÁ - API & E2E Testing Suite

Este repositorio contiene la API del sistema **Nayá** junto con una suite completa de pruebas End-to-End (E2E) automatizadas para verificar el comportamiento de los flujos de autenticación, gestión de perfiles e integración de pacientes y terapeutas.

---

## 👥 Integrantes del Equipo

Los integrantes que han contribuido al desarrollo de este proyecto (según el historial de contribuciones de Git) son:

* Diego Rivera Cisneros
* Eduardo Osvaldo Rodriguez Guitierrez
* Rodrigo Vega Espinoza
* Annatar Armando Murillo Rivera

---

## 🛠️ Herramienta Utilizada

Para la suite de pruebas E2E se ha seleccionado **Playwright** para API Testing.

### ¿Por qué Playwright en lugar de Maestro?
1. **Especialización y Robustez en API**: Playwright proporciona un `APIRequestContext` nativo extremadamente rápido y versátil para realizar peticiones HTTP directas y validar respuestas.
2. **Soporte Nativo de TypeScript**: Permite crear una suite robusta con tipado estático, reduciendo errores en tiempo de escritura.
3. **Reportes Visuales Detallados**: Genera reportes HTML interactivos con trazas, tiempos de respuesta y detalles de las llamadas.
4. **Integración con CI/CD**: Se configura fácilmente en entornos de integración continua como GitHub Actions.

---

## 📦 Instrucciones de Instalación y Ejecución

### 1. Requisitos Previos
* **Python** 3.11+ instalado localmente.
* **Node.js** 16+ y **npm** (para la ejecución de las pruebas).
* **Docker y Docker Compose** (opcional, para ejecución rápida).

---

### 2. Levantamiento de la API (Backend)

Puedes iniciar la API de dos maneras:

#### Opción A: Utilizando Docker Compose (Recomendado)
Desde la raíz del proyecto ejecuta:
```bash
docker-compose up --build
```
Esto levantará de forma automática la base de datos PostgreSQL, Redis, PgAdmin y la aplicación FastAPI en `http://localhost:8000`.

#### Opción B: Ejecución Manual Local
1. Crea y activa un entorno virtual de Python:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura tus variables de entorno copiando el archivo `.env.example` a un nuevo archivo `.env` y modificando sus valores si es necesario.
4. Ejecuta las migraciones de base de datos con Alembic:
   ```bash
   alembic upgrade head
   ```
5. Inicia el servidor de desarrollo:
   ```bash
   uvicorn app.main:app --reload
   ```
   La API estará disponible en `http://localhost:8000`.

---

### 3. Instalación de la Suite de Pruebas E2E

1. Dirígete al directorio de pruebas:
   ```bash
   cd e2e-tests
   ```
2. Ejecuta el script de configuración automática para instalar dependencias y navegadores:
   * **En Windows (PowerShell):**
     ```powershell
     .\setup.bat
     ```
   * **En macOS/Linux:**
     ```bash
     chmod +x setup.sh
     ./setup.sh
     ```
   *(Alternativamente, puedes ejecutar manualmente `npm install` seguido de `npx playwright install`).*

---

### 4. Ejecución de las Pruebas E2E

Desde la carpeta `e2e-tests`, utiliza los siguientes comandos:

* **Ejecutar todos los flujos:**
  ```bash
  npm test
  ```
* **Ejecutar pruebas y abrir el reporte HTML interactivo:**
  ```bash
  npm test
  npm run test:report
  ```
* **Ejecutar en modo interactivo UI (Playwright UI):**
  ```bash
  npm run test:ui
  ```
* **Ejecutar en modo Debug (paso a paso):**
  ```bash
  npm run test:debug
  ```

---

##  Descripción de los 6 Flujos Automatizados

La suite valida 6 flujos significativos del ciclo de vida del usuario dentro de Nayá:

###  FLOW 1: Registro de Paciente y Verificación de Email
* **Descripción**: Valida que un nuevo paciente pueda registrarse exitosamente cumpliendo con políticas de seguridad (contraseñas seguras, emails únicos) y que el código de verificación sea procesado correctamente.
* **Endpoints**: `POST /api/v1/patients` → `POST /api/v1/auth/verification-code`

###  FLOW 2: Login y Obtención de JWT
* **Descripción**: Verifica las credenciales del usuario registrado y asegura la correcta emisión de los tokens `access_token` y `refresh_token`, comprobando además que se pueda acceder a un endpoint protegido (`/api/v1/auth/daily`) adjuntando el JWT obtenido.
* **Endpoints**: `POST /api/v1/auth/login` → `GET /api/v1/auth/daily`

###  FLOW 3: Solicitud de Código de Reseteo de Contraseña
* **Descripción**: Simula la solicitud de recuperación de contraseña por parte de un usuario que olvidó sus credenciales, verificando que la API procese el email y genere un código temporal de recuperación.
* **Endpoints**: `POST /api/v1/auth/password-change-request`

###  FLOW 4: Validación de Código de Reseteo de Contraseña
* **Descripción**: Comprueba que el código de reseteo sea validado de forma correcta por el servidor y que se rechacen códigos expirados o inválidos.
* **Endpoints**: `POST /api/v1/auth/verification-code-password-reset`

###  FLOW 5: Reseteo de Contraseña
* **Descripción**: Ejecuta el cambio final de la contraseña utilizando el código de verificación validado, corroborando que se apliquen las reglas de fortaleza de contraseña y que el usuario pueda hacer login posterior con sus nuevas credenciales.
* **Endpoints**: `PUT /api/v1/auth/password-reset`

###  FLOW 6: Conexión con Terapeuta + Perfil + Obtención de Consejo Diario
* **Descripción**: Representa la interacción avanzada del flujo del negocio donde un paciente ya logueado asocia su cuenta a un terapeuta mediante un código, configura su avatar (perfil animal) y accede a su consejo diario personalizado en la aplicación.
* **Endpoints**: 
  * `POST /api/v1/auth/connect-patient-with-therapist`
  * `POST /api/v1/auth/select-profile`
  * `GET /api/v1/auth/daily`

---

##  Evidencia de Ejecución de Pruebas

Al ejecutar el comando `npm test` en el directorio `e2e-tests`, se procesan de forma consecutiva e independiente todos los casos de prueba definidos en `tests/auth.spec.ts`, incluyendo casos de éxito y de control de errores:

```text
running 12 tests using 1 worker

✓ FLOW 1.1: Register new patient with valid data (1.5s)
✓ FLOW 1.2: Validate verification code for email (0.8s)
✓ FLOW 2.1: Login with valid credentials returns JWT (1.2s)
✓ FLOW 2.2: Verify JWT token is valid for protected endpoints (0.9s)
✓ FLOW 3.1: Request password reset verification code (1.1s)
✓ FLOW 4.1: Validate password reset verification code (1.0s)
✓ FLOW 5.1: Reset password with new password (1.3s)
✓ FLOW 6.1: Connect patient with therapist using connection code (1.4s)
✓ FLOW 6.2: Select profile picture with animal ID (0.8s)
✓ FLOW 6.3: Get daily advice (protected endpoint) (0.9s)
✓ ERROR: Login with invalid email returns 401 (0.8s)
✓ ERROR: Register with duplicate email returns 403 (1.1s)

12 passed (12.5s)
```

> [!TIP]
> Los reportes completos e interactivos con detalles de cada request y response están disponibles en la carpeta `e2e-tests/playwright-report/` después de cada corrida.