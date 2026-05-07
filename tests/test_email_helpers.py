"""
Tests para utilidades de app.utils.email:
- _email_domain extrae el dominio sin fugar el local-part del email.
- Las constantes de eventos están definidas y son strings inmutables.

No tocan SMTP real; los flujos de envío se cubren en otros tests con mocks.
"""
from app.utils import email as email_module


class TestEmailDomain:
    def test_returns_domain_part(self):
        assert email_module._email_domain("juan@gmail.com") == "gmail.com"

    def test_returns_marker_when_no_at_sign(self):
        assert email_module._email_domain("not-an-email") == "<no-domain>"

    def test_handles_subdomain(self):
        assert email_module._email_domain("a@mail.gmail.com") == "mail.gmail.com"

    def test_does_not_leak_local_part(self):
        # Garantía explícita: el output NO contiene el local-part del email,
        # para que sea seguro loguearlo en Sentry sin filtrar PII.
        domain = email_module._email_domain("sensible.usuario@gmail.com")
        assert "sensible.usuario" not in domain
        assert domain == "gmail.com"


class TestEventConstants:
    def test_all_event_constants_are_strings(self):
        assert isinstance(email_module._EVT_EMAIL_SENT, str)
        assert isinstance(email_module._EVT_EMAIL_SMTP_FAILED, str)
        assert isinstance(email_module._EVT_EMAIL_SEND_FAILED, str)

    def test_event_names_use_dot_namespace(self):
        # Convención: eventos del logger usan "<dominio>.<accion>".
        for evt in (
            email_module._EVT_EMAIL_SENT,
            email_module._EVT_EMAIL_SMTP_FAILED,
            email_module._EVT_EMAIL_SEND_FAILED,
        ):
            assert evt.startswith("email.")
            # debe haber acción después del namespace
            assert len(evt) > len("email.")

    def test_constants_are_unique(self):
        # Si dos eventos colisionaran, perderíamos especificidad en Sentry.
        events = {
            email_module._EVT_EMAIL_SENT,
            email_module._EVT_EMAIL_SMTP_FAILED,
            email_module._EVT_EMAIL_SEND_FAILED,
        }
        assert len(events) == 3
