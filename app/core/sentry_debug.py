"""
Endpoints de diagnóstico que provocan errores realistas para validar la
captura de Sentry. Cada endpoint genera un tipo de error distinto, así se
ve cómo se agrupan los Issues en Sentry.

Solo se registra si `SENTRY_ENVIRONMENT != production`. En production los
endpoints devuelven 404 (manejado al registrar el router).

Uso desde curl:
    curl -X POST http://localhost:8000/sentry-debug/<error-type>

Tipos disponibles:
    /sentry-debug                    → ZeroDivisionError
    /sentry-debug/attribute-error    → AttributeError (None.foo)
    /sentry-debug/key-error          → KeyError (dict[missing])
    /sentry-debug/value-error        → ValueError (UUID inválido)
    /sentry-debug/type-error         → TypeError (str + int)
    /sentry-debug/index-error        → IndexError (lista vacía)
    /sentry-debug/db-bad-query       → SQLAlchemy ProgrammingError
    /sentry-debug/db-integrity       → IntegrityError (UNIQUE violation)
    /sentry-debug/log-error          → logger.error con exc_info (Sentry via Logging)
    /sentry-debug/captured-message   → sentry_sdk.capture_message manual
    /sentry-debug/with-user-context  → error con datos de usuario en el evento
"""
from __future__ import annotations

import logging
from uuid import UUID, uuid4

import sentry_sdk
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.database import SessionDep
from app.core.logger import logger

sentry_debug_router = APIRouter(prefix="/sentry-debug", tags=["Sentry Debug"])


@sentry_debug_router.post("/attribute-error", include_in_schema=False)
async def attribute_error():
    """Simula acceso a un atributo de un objeto que es None — caso típico
    cuando una query devuelve None y el código asume que existe."""
    user = None  # típicamente vendría de session.get(...)
    return {"name": user.name}  # AttributeError: 'NoneType' object has no attribute 'name'


@sentry_debug_router.post("/key-error", include_in_schema=False)
async def key_error():
    """Simula un payload externo (ej. JWT, API de terceros) que no trae
    el campo que esperamos."""
    payload = {"sub": "abc", "exp": 999}
    return {"role": payload["role"]}  # KeyError: 'role'


@sentry_debug_router.post("/value-error", include_in_schema=False)
async def value_error():
    """UUID malformado pasado por el frontend."""
    return {"id": UUID("not-a-uuid")}  # ValueError: badly formed hexadecimal


@sentry_debug_router.post("/type-error", include_in_schema=False)
async def type_error():
    """Operación entre tipos incompatibles — típico al concatenar score
    int con un texto sin convertir."""
    score = 88
    return {"msg": "Score: " + score}  # TypeError: can only concatenate str


@sentry_debug_router.post("/index-error", include_in_schema=False)
async def index_error():
    """Acceder al primer elemento de una lista vacía — caso del bug que
    encontramos en /auth/daily al inicio."""
    advices = []
    return {"advice": advices[0]}  # IndexError: list index out of range


@sentry_debug_router.post("/db-bad-query", include_in_schema=False)
async def db_bad_query(session: SessionDep):
    """Query a una tabla inexistente — simula el error que vimos cuando
    no había migraciones aplicadas."""
    session.exec(text("SELECT * FROM tabla_que_no_existe"))
    return {"ok": False}


@sentry_debug_router.post("/db-integrity", include_in_schema=False)
async def db_integrity(session: SessionDep):
    """Viola FK constraint: parent_child con patient_id inexistente."""
    fake_user = uuid4()
    fake_patient = uuid4()
    session.exec(
        text(
            "INSERT INTO parent_child (id, parent_user_id, patient_id, created_at, updated_at) "
            "VALUES (:id, :u, :p, NOW(), NOW())"
        ).bindparams(id=uuid4(), u=fake_user, p=fake_patient)
    )
    session.commit()
    return {"ok": False}


@sentry_debug_router.post("/log-error", include_in_schema=False)
async def log_error_no_raise():
    """logger.error con exc_info → Sentry lo captura via LoggingIntegration
    aunque no se haga raise. Útil para 'errores silenciosos'."""
    try:
        x = {}["missing_key"]
    except Exception:
        logger.error(
            "background_task.failed",
            extra={"event": "background_task.failed", "task": "process_emotion_results"},
            exc_info=True,
        )
    return {"status": "logged_only", "note": "Sentry should still capture it"}


@sentry_debug_router.post("/captured-message", include_in_schema=False)
async def captured_message():
    """Mensaje no-error que llega a Sentry como evento de severidad 'warning'.
    Útil para señales de negocio (ej. abuso detectado, rate-limit, etc)."""
    sentry_sdk.capture_message(
        "Suspicious activity detected: 5 failed login attempts in 1 minute",
        level="warning",
    )
    return {"status": "message_sent"}


@sentry_debug_router.post("/with-user-context", include_in_schema=False)
async def with_user_context():
    """Error con scope: agrega user/tag/extra que aparecerán en el evento
    de Sentry para facilitar el diagnóstico."""
    with sentry_sdk.new_scope() as scope:
        scope.set_user({"id": "demo-user-123", "username": "sofia"})
        scope.set_tag("flow", "memociones")
        scope.set_extra("game_session", {"pairs_matched": 3, "duration_seconds": 45})
        # Error real adentro del scope
        scores = [80, 75]
        return {"avg": sum(scores) / scores[2]}  # IndexError captura todo el scope


@sentry_debug_router.post("/timeout-simulation", include_in_schema=False)
async def timeout_simulation():
    """Simula un fallo por timeout en una llamada externa (ej. SMTP/email)."""
    raise TimeoutError(
        "SMTP server smtp.gmail.com did not respond within 30s while sending verification code"
    )


@sentry_debug_router.post("/business-rule-violation", include_in_schema=False)
async def business_rule_violation():
    """Error de regla de negocio: un niño con energía 0 intenta jugar.
    No es un crash, pero queremos que Sentry lo registre como warning."""
    sentry_sdk.capture_message(
        "Patient attempted to start activity with 0 energy",
        level="warning",
    )
    raise HTTPException(
        status_code=400,
        detail={"message": "no_more_energy", "code": "ENERGY_DEPLETED"},
    )
