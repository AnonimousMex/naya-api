"""
Tests para los endpoints de sentry_debug_router. Cada endpoint genera
un error específico — verificamos que el endpoint efectivamente lo
levanta (Sentry lo captura via LoggingIntegration en producción).

Usamos TestClient con una app FastAPI mínima que monta el router.
"""
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.sentry_debug import sentry_debug_router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(sentry_debug_router)
    return TestClient(app, raise_server_exceptions=False)


class TestSentryDebugErrors:
    def test_attribute_error_returns_500(self, client):
        r = client.post("/sentry-debug/attribute-error")
        assert r.status_code == 500

    def test_key_error_returns_500(self, client):
        r = client.post("/sentry-debug/key-error")
        assert r.status_code == 500

    def test_value_error_returns_500(self, client):
        r = client.post("/sentry-debug/value-error")
        assert r.status_code == 500

    def test_type_error_returns_500(self, client):
        r = client.post("/sentry-debug/type-error")
        assert r.status_code == 500

    def test_index_error_returns_500(self, client):
        r = client.post("/sentry-debug/index-error")
        assert r.status_code == 500


class TestSentryDebugLogPaths:
    def test_log_error_returns_200(self, client):
        # Este path NO levanta — solo loguea con exc_info.
        r = client.post("/sentry-debug/log-error")
        assert r.status_code == 200
        assert r.json()["status"] == "logged_only"

    def test_captured_message_returns_200(self, client):
        with patch("app.core.sentry_debug.sentry_sdk") as fake_sdk:
            r = client.post("/sentry-debug/captured-message")
        assert r.status_code == 200
        fake_sdk.capture_message.assert_called_once()


class TestSentryDebugWithUserContext:
    def test_with_user_context_raises_500(self, client):
        # Tiene un IndexError adentro del scope.
        r = client.post("/sentry-debug/with-user-context")
        assert r.status_code == 500


class TestSentryDebugTimeoutAndBusinessRule:
    def test_timeout_simulation_returns_500(self, client):
        r = client.post("/sentry-debug/timeout-simulation")
        assert r.status_code == 500

    def test_business_rule_violation_returns_400(self, client):
        with patch("app.core.sentry_debug.sentry_sdk"):
            r = client.post("/sentry-debug/business-rule-violation")
        assert r.status_code == 400
        body = r.json()
        # FastAPI HTTPException pone el detail tal cual
        assert body["detail"]["code"] == "ENERGY_DEPLETED"
