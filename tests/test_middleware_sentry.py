"""
Tests para `_enrich_sentry_scope` del RequestContextMiddleware.

Garantizan que:
- Sin Authorization header no hace nada (no toca Sentry).
- Con un JWT válido setea `sentry_sdk.set_user` con id/username/user_type.
- Con un token inválido NO crashea (defensiva: observabilidad nunca rompe app).
- Setea tags request_id/path/method en Sentry.
"""
from unittest.mock import MagicMock, patch

from app.core.middleware import _enrich_sentry_scope
from app.utils.security import create_access_token


def _fake_request(*, headers: dict | None = None, path: str = "/api/v1/games", method: str = "GET"):
    """Construye un Request fake mínimo (sin Starlette real)."""
    req = MagicMock()
    req.headers = headers or {}
    req.url.path = path
    req.method = method
    return req


class TestEnrichSentryScope:
    def test_no_auth_header_only_sets_request_tags(self):
        request = _fake_request(headers={})
        with patch("app.core.middleware.sentry_sdk") as fake_sentry:
            _enrich_sentry_scope(request, "rid-123")

        # Tags básicos sí, pero set_user NO debe llamarse.
        fake_sentry.set_tag.assert_any_call("request_id", "rid-123")
        fake_sentry.set_tag.assert_any_call("path", "/api/v1/games")
        fake_sentry.set_tag.assert_any_call("method", "GET")
        fake_sentry.set_user.assert_not_called()

    def test_valid_jwt_sets_user(self):
        # Genero un token real para no andar mockeando jwt.decode.
        from app.constants.user_constants import UserRoles
        from types import SimpleNamespace

        fake_user = SimpleNamespace(
            id="11111111-1111-1111-1111-111111111111",
            email="t@example.com",
            name="Tester",
        )
        fake_user.patient = None
        fake_user.therapist = None

        token = create_access_token(
            user_data={
                "user_id": str(fake_user.id),
                "email": fake_user.email,
                "name": fake_user.name,
                "user_type": UserRoles.PATIENT.value,
            },
        )

        request = _fake_request(headers={"authorization": f"Bearer {token}"})
        with patch("app.core.middleware.sentry_sdk") as fake_sentry:
            _enrich_sentry_scope(request, "rid-abc")

        fake_sentry.set_user.assert_called_once()
        user_payload = fake_sentry.set_user.call_args[0][0]
        assert user_payload["id"] == str(fake_user.id)
        assert user_payload["username"] == "Tester"
        assert user_payload["user_type"] == UserRoles.PATIENT.value

    def test_invalid_token_does_not_raise(self):
        request = _fake_request(headers={"authorization": "Bearer not-a-real-jwt"})
        with patch("app.core.middleware.sentry_sdk") as fake_sentry:
            # No debe levantar nada — observabilidad es best-effort.
            _enrich_sentry_scope(request, "rid-xyz")
        # Tags básicos se setean pero set_user no.
        fake_sentry.set_user.assert_not_called()

    def test_missing_authorization_header_capitalization_variants(self):
        # `headers.get("authorization") or get("Authorization")` debería
        # encontrar el header con cualquier caso.
        for header_name in ("authorization", "Authorization"):
            request = _fake_request(headers={header_name: "Bearer xyz"})
            with patch("app.core.middleware.sentry_sdk"):
                # No raise: ese es el contrato.
                _enrich_sentry_scope(request, "rid-1")

    def test_observability_failure_is_swallowed(self):
        # Si sentry_sdk.set_tag explota por algún motivo, la app no debe verlo.
        request = _fake_request(headers={})
        with patch("app.core.middleware.sentry_sdk") as fake_sentry:
            fake_sentry.set_tag.side_effect = RuntimeError("sentry boom")
            # No raise.
            _enrich_sentry_scope(request, "rid-1")
