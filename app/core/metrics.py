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
