"""
Métricas Prometheus personalizadas de la API Naya.

Todas las métricas custom usan el prefijo `naya_` para diferenciarlas
de las HTTP autogeneradas por prometheus-fastapi-instrumentator.

Uso:
    from app.core import metrics
    metrics.LOGIN_SUCCESS.inc()
    metrics.AUTH_FAILURES.labels(reason="invalid_password").inc()
    with metrics.CRITICAL_OP_DURATION.labels(operation="register_user").time():
        ...
"""
from prometheus_client import Counter, Gauge, Histogram

# --- Auth ---------------------------------------------------------------

LOGIN_SUCCESS = Counter(
    "naya_login_success_total",
    "Logins exitosos",
    ["role"],
)

AUTH_FAILURES = Counter(
    "naya_auth_failures_total",
    "Fallos de autenticación",
    ["reason"],
)

VERIFICATION_CODES_GENERATED = Counter(
    "naya_verification_codes_generated_total",
    "Códigos de verificación generados",
    ["kind"],  # signup | password_reset | connection
)

# --- Usuarios y conexiones ---------------------------------------------

USERS_REGISTERED = Counter(
    "naya_users_registered_total",
    "Usuarios registrados por rol",
    ["role"],  # patient | therapist | parent
)

PATIENT_THERAPIST_CONNECTIONS = Counter(
    "naya_patient_therapist_connections_total",
    "Conexiones paciente-terapeuta creadas",
)

# --- Tests / respuestas ------------------------------------------------

TESTS_STARTED = Counter(
    "naya_tests_started_total",
    "Tests iniciados",
)

TEST_ANSWERS = Counter(
    "naya_test_answers_total",
    "Respuestas de test registradas",
)

# --- Activity results & métricas por audiencia -------------------------

ACTIVITY_RESULTS = Counter(
    "naya_activity_results_total",
    "Resultados de actividad registrados",
    ["role"],  # patient | system | etc
)

METRICS_VIEW = Counter(
    "naya_metrics_view_total",
    "Consultas de métricas por audiencia",
    ["audience"],  # therapist | tutor
)

METRICS_RECALCULATIONS = Counter(
    "naya_metrics_recalculations_total",
    "Solicitudes de recálculo de métricas (operación administrativa)",
)

# Score reportado por el cliente al cerrar una actividad. Histogram con
# buckets útiles para distribución (heatmap en Grafana).
ACTIVITY_SCORE = Histogram(
    "naya_activity_score",
    "Distribución de scores reportados al cerrar actividades",
    buckets=(10, 20, 30, 40, 50, 60, 70, 80, 90, 100),
)

# Duración real de una sesión de actividad (segundos). Útil para detectar
# actividades demasiado cortas (skipped) o demasiado largas (atascadas).
ACTIVITY_DURATION = Histogram(
    "naya_activity_duration_seconds_observed",
    "Duración observada de actividades cerradas",
    buckets=(15, 30, 60, 120, 180, 300, 600, 900, 1800),
)

# Cuenta cada vez que una respuesta se asocia a una emoción. Permite ver
# qué emociones predominan en respuestas a nivel global.
EMOTIONS_DETECTED = Counter(
    "naya_emotions_detected_total",
    "Emociones detectadas en respuestas registradas",
    ["emotion"],  # Miedo | Tristeza | Felicidad | Enojo | Vergüenza
)

# Cuenta cada vez que una respuesta lleva una categoría de afrontamiento.
COPING_RECORDED = Counter(
    "naya_coping_recorded_total",
    "Categorías de afrontamiento reportadas",
    ["category"],  # avoidance | frustration | abandonment
)

# --- Juegos -------------------------------------------------------------

GAMES_STARTED = Counter(
    "naya_games_started_total",
    "Sesiones de juego iniciadas (cuando el cliente consume una vida)",
    ["game"],  # detective | memociones | y_ese_ruido | otros
)

GAMES_COMPLETED = Counter(
    "naya_games_completed_total",
    "Resultados al cerrar una sesión de juego",
    ["game", "outcome"],  # outcome: success | failed | abandoned
)

# --- Energy / vidas -----------------------------------------------------

ENERGY_CONSUMED = Counter(
    "naya_energy_consumed_total",
    "Vidas consumidas exitosamente (al iniciar una actividad)",
)

ENERGY_DEPLETED = Counter(
    "naya_energy_depleted_total",
    "Intentos de consumir vida cuando el usuario ya no tiene energía",
)

ENERGY_RECHARGED_UNITS = Counter(
    "naya_energy_recharged_units_total",
    "Unidades de vida recargadas automáticamente por el reloj de la API",
)

# --- Citas / appointments ----------------------------------------------

APPOINTMENTS_CREATED = Counter(
    "naya_appointments_created_total",
    "Citas creadas por el terapeuta",
)

APPOINTMENTS_CANCELLED = Counter(
    "naya_appointments_cancelled_total",
    "Citas canceladas",
)

APPOINTMENTS_RESCHEDULED = Counter(
    "naya_appointments_rescheduled_total",
    "Citas reagendadas",
)

APPOINTMENTS_COMPLETED = Counter(
    "naya_appointments_completed_total",
    "Citas marcadas como completadas",
)

APPOINTMENT_CONFLICTS = Counter(
    "naya_appointment_conflicts_total",
    "Intentos de agenda con choque de horario",
    ["operation"],  # create | reschedule
)

# --- Email --------------------------------------------------------------

EMAILS_SENT = Counter(
    "naya_emails_sent_total",
    "Emails enviados con éxito",
    ["kind"],  # verification | connection_code | password_reset
)

EMAIL_FAILURES = Counter(
    "naya_email_failures_total",
    "Fallos al enviar email",
    ["kind", "reason"],  # reason: smtp | other
)

# --- Conexiones rechazadas (paciente ↔ terapeuta) ----------------------

THERAPIST_CONNECTION_REJECTED = Counter(
    "naya_therapist_connection_rejected_total",
    "Intentos de conexión paciente-terapeuta rechazados",
    ["reason"],  # unknown_code | unknown_patient | already_linked
)

# --- Errores por módulo ------------------------------------------------

MODULE_ERRORS = Counter(
    "naya_module_errors_total",
    "Errores no controlados por módulo",
    ["module"],
)

# --- Operaciones críticas ----------------------------------------------

CRITICAL_OP_DURATION = Histogram(
    "naya_critical_op_duration_seconds",
    "Duración de operaciones críticas",
    ["operation"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

# --- Estado de la API --------------------------------------------------

API_UP = Gauge(
    "naya_api_up",
    "1 si la API está lista (post-startup)",
)

DB_CONNECTION_ERRORS = Counter(
    "naya_db_connection_errors_total",
    "Fallos al conectar a la base de datos",
)
