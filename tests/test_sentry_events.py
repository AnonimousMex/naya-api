"""
Tests para los helpers de app.core.sentry_events.

Estos helpers envuelven sentry_sdk con la promesa de que NUNCA rompen
el request si Sentry está inactivo, mal configurado, o si tira un
error inesperado. Aquí cubrimos:

- breadcrumb()  → llama add_breadcrumb con args correctos.
- track()       → llama capture_message dentro de un new_scope con tags.
- set_user()    → arma payload sin PII y llama set_user.

Y para los 3, que cualquier excepción del sdk sea tragada (best-effort).
"""
from unittest.mock import MagicMock, patch

from app.core import sentry_events as sentry


class TestBreadcrumb:
    def test_calls_add_breadcrumb_with_args(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            sentry.breadcrumb(
                "auth",
                "login.attempt",
                level="info",
                data={"email_domain": "naya.local"},
            )

        fake_sdk.add_breadcrumb.assert_called_once_with(
            category="auth",
            message="login.attempt",
            level="info",
            data={"email_domain": "naya.local"},
        )

    def test_no_data_passes_none(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            sentry.breadcrumb("auth", "login.attempt")
        # Cuando data es None se preserva ese None — no convertir a {}.
        kwargs = fake_sdk.add_breadcrumb.call_args.kwargs
        assert kwargs["data"] is None

    def test_swallows_sdk_exceptions(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            fake_sdk.add_breadcrumb.side_effect = RuntimeError("sdk down")
            # Si esto levanta, falla el test.
            sentry.breadcrumb("auth", "x")

    def test_default_level_is_info(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            sentry.breadcrumb("c", "m")
        assert fake_sdk.add_breadcrumb.call_args.kwargs["level"] == "info"


class TestTrack:
    def test_capture_message_called(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            scope = MagicMock()
            fake_sdk.new_scope.return_value.__enter__.return_value = scope
            sentry.track(
                "user.registered",
                level="info",
                category="onboarding",
                tags={"role": "PATIENT"},
                extras={"user_id": "abc"},
            )

        fake_sdk.capture_message.assert_called_once_with(
            "user.registered", level="info"
        )
        # category se setea como tag explícitamente
        scope.set_tag.assert_any_call("category", "onboarding")
        scope.set_tag.assert_any_call("role", "PATIENT")
        scope.set_extra.assert_any_call("user_id", "abc")

    def test_no_category_does_not_set_category_tag(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            scope = MagicMock()
            fake_sdk.new_scope.return_value.__enter__.return_value = scope
            sentry.track("evt")
        # El tag "category" no debe haber sido seteado
        for call in scope.set_tag.call_args_list:
            assert call.args[0] != "category"

    def test_swallows_exceptions(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            fake_sdk.new_scope.side_effect = RuntimeError("oops")
            sentry.track("evt")  # no debe relanzar


class TestSetUser:
    def test_sets_user_with_id_role_domain(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            sentry.set_user(
                user_id="123", role="PATIENT", email_domain="naya.local"
            )
        fake_sdk.set_user.assert_called_once_with(
            {"id": "123", "user_type": "PATIENT", "email_domain": "naya.local"}
        )

    def test_no_args_does_not_call_set_user(self):
        # Si no hay nada que setear, no llamamos al sdk (evita borrar info previa).
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            sentry.set_user()
        fake_sdk.set_user.assert_not_called()

    def test_partial_payload_only_includes_provided_fields(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            sentry.set_user(user_id="42")
        payload = fake_sdk.set_user.call_args.args[0]
        assert payload == {"id": "42"}

    def test_swallows_exceptions(self):
        with patch("app.core.sentry_events.sentry_sdk") as fake_sdk:
            fake_sdk.set_user.side_effect = RuntimeError("boom")
            sentry.set_user(user_id="x")  # no relanzar
