"""
Middleware de observabilidad:
- Genera/propaga X-Request-ID y lo inyecta en contextvars (lo usa el logger).
- Loguea entrada y salida de cada request con duración.
- Cuenta excepciones no controladas en metrics.MODULE_ERRORS.
- Adjunta user (id, role) al scope de Sentry si el request trae JWT válido,
  para que cada evento de Sentry quede atado al usuario sin tocar controllers.
"""
import time
import uuid

import sentry_sdk
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core import metrics
from app.core.logger import logger, request_id_ctx


def _enrich_sentry_scope(request: Request, request_id: str) -> None:
    """
    Setea user/tags en Sentry de forma defensiva:
    cualquier fallo aquí NUNCA debe romper el request.
    """
    try:
        sentry_sdk.set_tag("request_id", request_id)
        sentry_sdk.set_tag("path", request.url.path)
        sentry_sdk.set_tag("method", request.method)

        auth_header = request.headers.get("authorization") or request.headers.get(
            "Authorization"
        )
        if not auth_header:
            return

        # Import diferido para evitar ciclos en arranque y no pagar costo cuando no hay token.
        from app.utils.security import decode_token

        decoded = decode_token(auth_header)
        if not decoded:
            return

        user_payload = decoded.get("user") or {}
        user_id = decoded.get("sub") or user_payload.get("user_id")
        if user_id:
            # `username` y `id` son los campos canónicos que Sentry indexa.
            sentry_sdk.set_user(
                {
                    "id": str(user_id),
                    "username": user_payload.get("name"),
                    "user_type": user_payload.get("user_type"),
                }
            )
            if user_payload.get("user_type"):
                sentry_sdk.set_tag("user_type", user_payload["user_type"])
    except Exception:  # noqa: BLE001 - observabilidad nunca rompe la app
        pass


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_ctx.set(rid)
        start = time.perf_counter()

        # Path normalizado para evitar fugar IDs en logs
        path = request.url.path
        method = request.method

        _enrich_sentry_scope(request, rid)

        # No spamear el endpoint /metrics
        if path != "/metrics":
            logger.info(
                "request.start",
                extra={"event": "request.start", "method": method, "path": path},
            )

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            metrics.MODULE_ERRORS.labels(module=_module_from_path(path)).inc()
            logger.exception(
                "request.error",
                extra={
                    "event": "request.error",
                    "method": method,
                    "path": path,
                    "duration_ms": round(elapsed_ms, 2),
                    "error": str(exc),
                },
            )
            request_id_ctx.reset(token)
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = rid

        if path != "/metrics":
            log = logger.warning if response.status_code >= 500 else (
                logger.info if response.status_code < 400 else logger.warning
            )
            log(
                "request.end",
                extra={
                    "event": "request.end",
                    "method": method,
                    "path": path,
                    "status": response.status_code,
                    "duration_ms": round(elapsed_ms, 2),
                },
            )

        if response.status_code >= 500:
            metrics.MODULE_ERRORS.labels(module=_module_from_path(path)).inc()

        request_id_ctx.reset(token)
        return response


def _module_from_path(path: str) -> str:
    """Extrae un nombre de módulo razonable de un path (`/api/v1/auth/login` -> `auth`)."""
    parts = [p for p in path.strip("/").split("/") if p]
    # api/v1/<module>/...
    if len(parts) >= 3 and parts[0] == "api":
        return parts[2]
    if parts:
        return parts[0]
    return "root"
