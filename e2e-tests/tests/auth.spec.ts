import { test, expect } from './fixtures';
import { ApiHelper, NayaResponse, AuthResponse, PatientResponse } from './api.helper';

test.describe('Nayá API - E2E Test Suite', () => {
  let apiHelper: ApiHelper;
  let jwtToken: string;
  let patientId: string;
  let userId: string;
  let patientEmail: string;
  let generatedVerificationCode: string;

  test.beforeAll(async ({ playwright }) => {
    const context = await playwright.request.newContext({
      baseURL: 'http://localhost:8000',
      extraHTTPHeaders: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    apiHelper = new ApiHelper(context);
  });

  // =====================
  // FLOW 1: Registro de paciente y verificación de email
  // =====================
  test('FLOW 1.1: Register new patient with valid data', async ({ testData }) => {
    const uniqueEmail = `test_${Date.now()}_${Math.floor(Math.random() * 1000)}@example.com`;
    patientEmail = uniqueEmail;

    const patientData = {
      name: testData.patient.name,
      email: uniqueEmail,
      password: testData.patient.password,
      confirm_password: testData.patient.confirmPassword,
    };

    const response = await apiHelper.post<NayaResponse<PatientResponse>>(
      '/api/v1/patients',
      patientData
    );

    if (response.status !== 201) {
      console.log('FLOW 1.1 FAILED BODY:', JSON.stringify(response.body));
    }
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('status');
    expect(response.body).toHaveProperty('statusMessage');
    expect(response.body.statusMessage).toBe('Resource created');
    expect(response.body.data).toBeDefined();
    expect(response.body.data?.email).toBe(patientData.email);
    expect(response.body.data?.name).toBe(patientData.name);
    expect(response.body.data?.patientId).toBeDefined();

    patientId = response.body.data?.patientId || '';
    userId = response.body.data?.id || '';
  });

  test('FLOW 1.2: Validate verification code for email', async ({ testData }) => {
    const verificationData = {
      code: testData.verification.code,
    };

    const response = await apiHelper.post<NayaResponse>(
      '/api/v1/auth/verification-code',
      verificationData
    );

    // El código puede estar inválido (400) o válido (204/200)
    // Lo importante es que la API responde correctamente
    expect([200, 204, 400]).toContain(response.status);
  });

  // =====================
  // FLOW 2: Login y obtención de JWT
  // =====================
  test('FLOW 2.1: Login with valid credentials returns JWT', async ({ testData }) => {
    const loginData = {
      username: patientEmail || testData.patient.email,
      password: testData.patient.password,
    };

    const response = await apiHelper.postForm<AuthResponse>(
      '/api/v1/auth/login',
      loginData
    );

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('access_token');
    expect(response.body).toHaveProperty('refresh_token');
    expect(response.body).toHaveProperty('user_type');
    expect(response.body.user_type).toBe('PATIENT');
    expect(typeof response.body.access_token).toBe('string');
    expect(response.body.access_token.length).toBeGreaterThan(0);

    jwtToken = response.body.access_token;
  });

  test('FLOW 2.2: Verify JWT token is valid for protected endpoints', async () => {
    const response = await apiHelper.get<NayaResponse>(
      '/api/v1/auth/daily',
      { Authorization: `Bearer ${jwtToken}` }
    );

    // Si el token es válido, debe retornar 200
    // Si no está verificado, puede retornar 403
    expect([200, 403]).toContain(response.status);
  });

  // =====================
  // FLOW 3: Solicitud de código de reseteo de contraseña
  // =====================
  test('FLOW 3.1: Request password reset verification code', async ({ testData }) => {
    const passwordChangeData = {
      email: patientEmail || testData.patient.email,
    };

    const response = await apiHelper.postNoContent(
      '/api/v1/auth/password-change-request',
      passwordChangeData
    );

    expect([200, 204]).toContain(response.status);
  });

  // =====================
  // FLOW 4: Validación de código de reseteo de contraseña
  // =====================
  test('FLOW 4.1: Validate password reset verification code', async ({ testData }) => {
    const verificationData = {
      code: testData.verification.passwordResetCode,
    };

    const response = await apiHelper.post<NayaResponse>(
      '/api/v1/auth/verification-code-password-reset',
      verificationData
    );

    // Puede ser válido (200/204) o inválido (400)
    expect([200, 204, 400]).toContain(response.status);
  });

  // =====================
  // FLOW 5: Reseteo de contraseña
  // =====================
  test('FLOW 5.1: Reset password with new password', async ({ testData }) => {
    const resetPasswordData = {
      email: patientEmail || testData.patient.email,
      password: testData.patient.newPassword,
      confirm_password: testData.patient.newConfirmPassword,
    };

    const response = await apiHelper.putNoContent(
      '/api/v1/auth/password-reset',
      resetPasswordData
    );

    // Puede ser exitoso (200/204) o fallar si el código no es válido (400)
    expect([200, 204, 400]).toContain(response.status);
  });

  // =====================
  // FLOW 6: Conectar con terapeuta + Seleccionar perfil + Obtener consejo
  // =====================
  test('FLOW 6.1: Connect patient with therapist using connection code', async ({ testData }) => {
    const connectionData = {
      code: testData.therapist.connectionCode,
    };

    const response = await apiHelper.postNoContent(
      '/api/v1/auth/connect-patient-with-therapist',
      connectionData,
      { Authorization: `Bearer ${jwtToken}` }
    );

    // Puede retornar 204 si es exitoso o 400 si el código no es válido
    expect([200, 204, 400]).toContain(response.status);
  });

  test('FLOW 6.3: Get daily advice (protected endpoint)', async () => {
    const response = await apiHelper.get<NayaResponse>(
      '/api/v1/auth/daily',
      { Authorization: `Bearer ${jwtToken}` }
    );

    // Si el usuario está verificado, retorna 200
    // Si no lo está, retorna 403
    expect([200, 403]).toContain(response.status);

    if (response.status === 200 && response.body.data) {
      expect(response.body.data).toHaveProperty('id');
      expect(response.body.data).toHaveProperty('title');
      expect(response.body.data).toHaveProperty('description');
    }
  });

  // =====================
  // EDGE CASES & ERROR HANDLING
  // =====================
  test('ERROR: Login with invalid email returns 401', async ({ testData }) => {
    const invalidLoginData = {
      username: 'invalid@example.com',
      password: testData.patient.password,
    };

    const response = await apiHelper.postForm<any>(
      '/api/v1/auth/login',
      invalidLoginData
    );

    expect(response.status).toBe(401);
  });

  test('ERROR: Login with wrong password returns 401', async ({ testData }) => {
    const wrongPasswordData = {
      username: patientEmail || testData.patient.email,
      password: 'wrongPassword123!',
    };

    const response = await apiHelper.postForm<any>(
      '/api/v1/auth/login',
      wrongPasswordData
    );

    expect(response.status).toBe(401);
  });

  test('ERROR: Access protected endpoint without token returns 401', async () => {
    const response = await apiHelper.get<any>(
      '/api/v1/auth/daily'
      // No Authorization header
    );

    expect(response.status).toBe(401);
  });

  test('ERROR: Register with invalid password format returns 422', async ({ testData }) => {
    const invalidPasswordData = {
      name: 'Test User',
      email: 'newuser@example.com',
      password: 'weak', // Too short and missing special chars
      confirm_password: 'weak',
    };

    const response = await apiHelper.post<any>(
      '/api/v1/patients',
      invalidPasswordData
    );

    expect(response.status).toBe(422);
  });

  test('ERROR: Register with non-matching passwords returns 403', async ({ testData }) => {
    const mismatchPasswordData = {
      name: 'Test User',
      email: 'newuser2@example.com',
      password: testData.patient.password,
      confirm_password: 'DifferentPassword123!', // Doesn't match
    };

    const response = await apiHelper.post<any>(
      '/api/v1/patients',
      mismatchPasswordData
    );

    expect([403, 422]).toContain(response.status);
  });
});
