"""
Logger estructurado JSON con propagación de request_id vía contextvars.

Mantiene compatibilidad con los imports existentes:
    from app.core.logger import logger
    logger.info("...")  # sigue funcionando

El request_id se inyecta automáticamente en cada registro siempre que
exista en el contexto (lo establece RequestContextMiddleware).
"""
import logging
import re
import sys
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger

# request_id por contexto (lo setea el middleware)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

# Campos sensibles que nunca deben aparecer en logs
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


def _truncate_token(value: str) -> str:
    """Deja sólo los primeros 6 chars del token para trazabilidad."""
    if len(value) <= 8:
        return "***"
    return f"{value[:6]}…(+{len(value) - 6})"


def _scrub(obj):
    """Limpia recursivamente claves sensibles y trunca tokens en strings."""
    if isinstance(obj, dict):
        return {
            k: ("***REDACTED***" if k.lower() in _SENSITIVE_KEYS else _scrub(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    if isinstance(obj, str):
        return _BEARER_RE.sub(lambda m: m.group(1) + _truncate_token(m.group(2)), obj)
    return obj


class _ContextFilter(logging.Filter):
    """Inyecta request_id y scrubbea campos sensibles en `extra`."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        # Scrub args y mensaje formateado
        if isinstance(record.args, dict):
            record.args = _scrub(record.args)
        if isinstance(record.msg, str):
            record.msg = _BEARER_RE.sub(
                lambda m: m.group(1) + _truncate_token(m.group(2)), record.msg
            )
        return True


class _JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("module", record.module)
        log_record.setdefault("line", record.lineno)
        log_record.setdefault("request_id", getattr(record, "request_id", "-"))
        # Scrub final por si algo sensible llegó por extra
        for k, v in list(log_record.items()):
            if k.lower() in _SENSITIVE_KEYS:
                log_record[k] = "***REDACTED***"
            elif isinstance(v, (dict, list, str)):
                log_record[k] = _scrub(v)


def setup_logger() -> logging.Logger:
    logger_ = logging.getLogger("naya_api")
    if logger_.handlers:
        return logger_  # idempotente
    logger_.setLevel(logging.INFO)
    logger_.propagate = False

    formatter = _JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "asctime": "ts", "name": "logger"},
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    ctx_filter = _ContextFilter()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.addFilter(ctx_filter)
    logger_.addHandler(console)

    file_handler = RotatingFileHandler(
        "naya_app.log", maxBytes=1_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ctx_filter)
    logger_.addHandler(file_handler)

    # Adjuntar el filtro a uvicorn para que comparta request_id
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv = logging.getLogger(name)
        uv.addFilter(ctx_filter)

    return logger_


logger = setup_logger()
