"""
Inicialización de Sentry para Naya API.

Diseño:
- Si `SENTRY_DSN` está vacío, init es no-op silencioso (no rompe nada en local
  sin Sentry configurado).
- Hooks `before_send` / `before_send_transaction` para:
  - Eliminar campos sensibles (password, token, authorization, jwt) del payload.
  - Truncar tokens Bearer dentro de strings.
  - Ignorar transacciones de `/metrics`, `/openapi.json`, `/docs`, `/redoc`.
- Adjunta `request_id` (de nuestro contextvar) como tag en cada evento, para
  poder pivotar de Sentry → logs estructurados.
- Integración con logging: `logger.error(..., exc_info=True)` se reporta a
  Sentry como evento. `logger.info` queda como breadcrumb.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.logger import request_id_ctx
from app.core.settings import settings


_SENSITIVE_KEYS = {
    "password",
    "passwd",
    "pwd",
    "token",
    "access_token",
    "refresh_token",
    "authorization",
    "secret",
    "jwt",
    "api_key",
    "apikey",
}
_BEARER_RE = re.compile(r"(Bearer\s+)([A-Za-z0-9._\-]+)", re.IGNORECASE)
_IGNORED_TRANSACTIONS = (
    "/metrics",
    "/api/v1/openapi.json",
    "/openapi.json",
    "/docs",
    "/redoc",
    "/favicon.ico",
)


def _truncate_token(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return f"{value[:6]}…(+{len(value) - 6})"


def _scrub(obj: Any) -> Any:
    """Scrub recursivo de claves sensibles y truncado de Bearer tokens."""
    if isinstance(obj, dict):
        return {
            k: ("***REDACTED***" if k.lower() in _SENSITIVE_KEYS else _scrub(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_scrub(v) for v in obj)
    if isinstance(obj, str):
        return _BEARER_RE.sub(
            lambda m: m.group(1) + _truncate_token(m.group(2)), obj
        )
    return obj


def _attach_request_id(event: Dict[str, Any]) -> None:
    rid = request_id_ctx.get()
    if rid and rid != "-":
        event.setdefault("tags", {})["request_id"] = rid


def _before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Se llama por cada evento de error antes de enviarse a Sentry."""
    _attach_request_id(event)
    # Scrub: request data, extras, contexts
    if "request" in event:
        event["request"] = _scrub(event["request"])
    if "extra" in event:
        event["extra"] = _scrub(event["extra"])
    if "contexts" in event:
        event["contexts"] = _scrub(event["contexts"])
    if "breadcrumbs" in event and event["breadcrumbs"].get("values"):
        event["breadcrumbs"]["values"] = [
            _scrub(b) for b in event["breadcrumbs"]["values"]
        ]
    return event


def _before_send_transaction(
    event: Dict[str, Any], hint: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Filtra transacciones ruidosas (Prometheus scrape, docs, etc)."""
    transaction = event.get("transaction") or ""
    if any(transaction.endswith(p) or transaction == p for p in _IGNORED_TRANSACTIONS):
        return None  # drop
    _attach_request_id(event)
    return event


def init_sentry() -> bool:
    """
    Inicializa Sentry si hay DSN. Devuelve True si quedó activo.
    Idempotente: llamadas repetidas son seguras.
    """
    dsn = (settings.SENTRY_DSN or "").strip()
    if not dsn:
        # Modo dev sin Sentry: no-op silencioso
        return False

    # `LoggingIntegration` por defecto:
    # - level=INFO captura logs de info como breadcrumbs.
    # - event_level=ERROR sube logs de error como eventos.
    logging_integration = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
    )

    sentry_sdk.init(
        dsn=dsn,
        environment=settings.SENTRY_ENVIRONMENT,
        release=settings.SENTRY_RELEASE,
        send_default_pii=False,  # NO mandar IPs/headers sensibles automáticamente
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        attach_stacktrace=True,
        max_breadcrumbs=50,
        before_send=_before_send,
        before_send_transaction=_before_send_transaction,
        integrations=[
            logging_integration,
            SqlalchemyIntegration(),
        ],
        # Tags globales: cualquier evento llevará estos
        # (project_name viene de settings, útil al tener varios servicios)
    )
    sentry_sdk.set_tag("project", settings.PROJECT_NAME)
    return True
