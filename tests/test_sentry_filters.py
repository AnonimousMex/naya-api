"""
Tests para los filtros de Sentry: scrubbing de PII, drop de transacciones
ruidosas, y attach del request_id como tag.
"""
from app.core.logger import request_id_ctx
from app.core.sentry import (
    _attach_request_id,
    _before_send,
    _before_send_transaction,
    _scrub,
    _truncate_token,
)


# El módulo `sentry` tiene sus propias copias de _scrub/_truncate (no
# comparte con logger.py). Validamos las dos por separado.


class TestSentryScrubBasics:
    def test_redacts_sensitive_keys(self):
        result = _scrub({"password": "x", "token": "y", "username": "u"})
        assert result["password"] == "***REDACTED***"
        assert result["token"] == "***REDACTED***"
        assert result["username"] == "u"

    def test_truncates_bearer_in_string(self):
        result = _scrub("Header: Bearer abcdef1234567890")
        assert "abcdef1234567890" not in result
        assert "abcdef" in result

    def test_preserves_tuples(self):
        result = _scrub((1, "Bearer abcdef1234567890", {"password": "x"}))
        assert isinstance(result, tuple)
        assert "abcdef" in result[1] and "1234567890" not in result[1]
        assert result[2]["password"] == "***REDACTED***"

    def test_truncate_short_token(self):
        assert _truncate_token("short") == "***"


class TestBeforeSend:
    def test_scrubs_request_data(self):
        event = {"request": {"data": {"password": "secret"}}}
        result = _before_send(event, hint={})
        assert result["request"]["data"]["password"] == "***REDACTED***"

    def test_scrubs_extra_block(self):
        event = {"extra": {"jwt": "xxxxx"}}
        result = _before_send(event, hint={})
        assert result["extra"]["jwt"] == "***REDACTED***"

    def test_scrubs_breadcrumbs(self):
        event = {
            "breadcrumbs": {
                "values": [
                    {"message": "Bearer abcdef1234567890token"},
                    {"data": {"password": "x"}},
                ]
            }
        }
        result = _before_send(event, hint={})
        b1, b2 = result["breadcrumbs"]["values"]
        assert "1234567890" not in b1["message"]
        assert b2["data"]["password"] == "***REDACTED***"

    def test_attaches_request_id_when_set(self):
        token = request_id_ctx.set("abc123def456")
        try:
            event = {}
            _before_send(event, hint={})
            assert event["tags"]["request_id"] == "abc123def456"
        finally:
            request_id_ctx.reset(token)

    def test_does_not_attach_when_request_id_default(self):
        # default es "-", no debe agregarse
        event = {}
        _before_send(event, hint={})
        assert "tags" not in event or "request_id" not in event.get("tags", {})


class TestBeforeSendTransaction:
    def test_drops_metrics_endpoint(self):
        assert _before_send_transaction({"transaction": "/metrics"}, {}) is None

    def test_drops_docs_endpoint(self):
        assert _before_send_transaction({"transaction": "/docs"}, {}) is None
        assert _before_send_transaction({"transaction": "/redoc"}, {}) is None

    def test_drops_openapi_json(self):
        assert _before_send_transaction({"transaction": "/api/v1/openapi.json"}, {}) is None
        assert _before_send_transaction({"transaction": "/openapi.json"}, {}) is None

    def test_drops_favicon(self):
        assert _before_send_transaction({"transaction": "/favicon.ico"}, {}) is None

    def test_passes_through_real_transactions(self):
        for path in ["/api/v1/animals", "/api/v1/auth/login", "/sentry-debug"]:
            event = {"transaction": path}
            result = _before_send_transaction(event, {})
            assert result is event  # mismo objeto, no None

    def test_attaches_request_id_to_transactions(self):
        token = request_id_ctx.set("xyz999")
        try:
            event = {"transaction": "/api/v1/animals"}
            result = _before_send_transaction(event, {})
            assert result["tags"]["request_id"] == "xyz999"
        finally:
            request_id_ctx.reset(token)


class TestAttachRequestId:
    def test_creates_tags_dict_if_missing(self):
        token = request_id_ctx.set("rid-1")
        try:
            event = {}
            _attach_request_id(event)
            assert event["tags"]["request_id"] == "rid-1"
        finally:
            request_id_ctx.reset(token)

    def test_preserves_existing_tags(self):
        token = request_id_ctx.set("rid-2")
        try:
            event = {"tags": {"existing": "value"}}
            _attach_request_id(event)
            assert event["tags"]["existing"] == "value"
            assert event["tags"]["request_id"] == "rid-2"
        finally:
            request_id_ctx.reset(token)
