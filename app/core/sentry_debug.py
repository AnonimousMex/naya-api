"""
Diagnostic endpoints that raise realistic errors to validate Sentry
capture. Each endpoint produces a distinct error type so we can see how
Issues are grouped in Sentry.

Only registered when `SENTRY_ENVIRONMENT != production`. In production
the endpoints respond 404 (gated when registering the router).

Usage from curl:
    curl -X POST http://localhost:8000/sentry-debug/<error-type>

Available types:
    /sentry-debug                    → ZeroDivisionError
    /sentry-debug/attribute-error    → AttributeError (None.foo)
    /sentry-debug/key-error          → KeyError (dict[missing])
    /sentry-debug/value-error        → ValueError (invalid UUID)
    /sentry-debug/type-error         → TypeError (str + int)
    /sentry-debug/index-error        → IndexError (empty list)
    /sentry-debug/db-bad-query       → SQLAlchemy ProgrammingError
    /sentry-debug/db-integrity       → IntegrityError (UNIQUE violation)
    /sentry-debug/log-error          → logger.error with exc_info (Sentry via Logging)
    /sentry-debug/captured-message   → manual sentry_sdk.capture_message
    /sentry-debug/with-user-context  → error with user payload attached
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
    """Simulates accessing an attribute on a None object — a common case
    when a query returns None and the code assumes the object exists."""
    user = None  # would normally come from session.get(...)
    return {"name": user.name}  # AttributeError: 'NoneType' object has no attribute 'name'


@sentry_debug_router.post("/key-error", include_in_schema=False)
async def key_error():
    """Simulates an external payload (e.g. JWT, third-party API) missing
    the field we expect."""
    payload = {"sub": "abc", "exp": 999}
    return {"role": payload["role"]}  # KeyError: 'role'


@sentry_debug_router.post("/value-error", include_in_schema=False)
async def value_error():
    """Malformed UUID sent by the frontend."""
    return {"id": UUID("not-a-uuid")}  # ValueError: badly formed hexadecimal


@sentry_debug_router.post("/type-error", include_in_schema=False)
async def type_error():
    """Operation between incompatible types — typical when concatenating
    an int score with a string without converting it."""
    score = 88
    return {"msg": "Score: " + score}  # TypeError: can only concatenate str


@sentry_debug_router.post("/index-error", include_in_schema=False)
async def index_error():
    """Accessing the first item of an empty list — same shape as the bug
    we found in /auth/daily early on."""
    advices = []
    return {"advice": advices[0]}  # IndexError: list index out of range


@sentry_debug_router.post("/db-bad-query", include_in_schema=False)
async def db_bad_query(session: SessionDep):
    """Query against a non-existent table — mirrors the failure mode we
    saw before migrations were applied."""
    session.exec(text("SELECT * FROM tabla_que_no_existe"))
    return {"ok": False}


@sentry_debug_router.post("/db-integrity", include_in_schema=False)
async def db_integrity(session: SessionDep):
    """Violates an FK constraint: parent_child with a non-existent patient_id."""
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
    """logger.error with exc_info → captured by Sentry through the
    LoggingIntegration even without re-raising. Useful for 'silent failures'."""
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
    """Non-error message reaching Sentry as a 'warning' severity event.
    Useful for business signals (e.g. abuse detected, rate-limit, etc)."""
    sentry_sdk.capture_message(
        "Suspicious activity detected: 5 failed login attempts in 1 minute",
        level="warning",
    )
    return {"status": "message_sent"}


@sentry_debug_router.post("/with-user-context", include_in_schema=False)
async def with_user_context():
    """Error inside a scope that carries user/tag/extra data — shows up
    on the Sentry event to make debugging easier."""
    with sentry_sdk.new_scope() as scope:
        scope.set_user({"id": "demo-user-123", "username": "sofia"})
        scope.set_tag("flow", "memociones")
        scope.set_extra("game_session", {"pairs_matched": 3, "duration_seconds": 45})
        # Real error inside the scope
        scores = [80, 75]
        return {"avg": sum(scores) / scores[2]}  # IndexError carries the whole scope


@sentry_debug_router.post("/timeout-simulation", include_in_schema=False)
async def timeout_simulation():
    """Simulates a timeout failure on an external call (e.g. SMTP/email)."""
    raise TimeoutError(
        "SMTP server smtp.gmail.com did not respond within 30s while sending verification code"
    )


@sentry_debug_router.post("/business-rule-violation", include_in_schema=False)
async def business_rule_violation():
    """Business rule violation: a child with 0 energy attempts to play.
    Not a crash, but we want Sentry to record it as a warning."""
    sentry_sdk.capture_message(
        "Patient attempted to start activity with 0 energy",
        level="warning",
    )
    raise HTTPException(
        status_code=400,
        detail={"message": "no_more_energy", "code": "ENERGY_DEPLETED"},
    )
