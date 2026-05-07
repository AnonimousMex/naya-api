"""
Tests para EmailService con SMTP completamente mockeado.

Cubren los caminos:
- Envío exitoso (logger.info "email.sent" + smtp.sendmail invocado).
- SMTPException (logger.error + internal_error).
- Excepción genérica (logger.exception + internal_error).
- Bug histórico: si SMTP() falla, mail.quit() en finally NO debe
  enmascarar la excepción original.

No tocamos el servidor SMTP real.
"""
import asyncio
import smtplib
from unittest.mock import MagicMock, patch

import pytest

from app.utils.email import EmailService


def _run(coro):
    """Helper para ejecutar coroutines en tests síncronos."""
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def patched_smtp():
    """Mock de smtplib.SMTP que se comporta como conexión exitosa."""
    with patch("app.utils.email.smtplib.SMTP") as fake_smtp_class:
        instance = MagicMock()
        fake_smtp_class.return_value = instance
        yield fake_smtp_class, instance


class TestSendVerificationEmailSuccess:
    def test_sendmail_invoked(self, patched_smtp):
        smtp_class, smtp_instance = patched_smtp
        _run(EmailService.send_verification_email(
            to_name="Pepe", to_email="pepe@naya.local", verification_code="123456"
        ))
        smtp_instance.sendmail.assert_called_once()
        # El destinatario aparece en los args
        args, _ = smtp_instance.sendmail.call_args
        assert "pepe@naya.local" in args

    def test_starttls_called(self, patched_smtp):
        _, smtp_instance = patched_smtp
        _run(EmailService.send_verification_email(
            to_name="Pepe", to_email="pepe@naya.local", verification_code="111"
        ))
        smtp_instance.starttls.assert_called_once()

    def test_quit_in_finally(self, patched_smtp):
        _, smtp_instance = patched_smtp
        _run(EmailService.send_verification_email(
            to_name="Pepe", to_email="pepe@naya.local", verification_code="111"
        ))
        smtp_instance.quit.assert_called_once()


class TestSendVerificationEmailFailure:
    def test_smtp_exception_is_caught(self):
        # Cuando login falla con SMTPException, internal_error se llama
        # y la excepción NO se propaga.
        with patch("app.utils.email.smtplib.SMTP") as fake_smtp_class, \
             patch("app.utils.email.NayaHttpResponse.internal_error") as fake_500:
            instance = MagicMock()
            instance.login.side_effect = smtplib.SMTPAuthenticationError(
                535, b"bad creds"
            )
            fake_smtp_class.return_value = instance

            _run(EmailService.send_verification_email(
                to_name="x", to_email="x@y.com", verification_code="z"
            ))
        fake_500.assert_called_once()

    def test_smtp_constructor_failure_does_not_raise_in_finally(self):
        # Bug histórico: si smtplib.SMTP() trona, mail queda en None.
        # El finally con mail.quit() rompía con AttributeError, ocultando
        # el error original. Verificamos que ya NO pase.
        with patch("app.utils.email.smtplib.SMTP") as fake_smtp_class, \
             patch("app.utils.email.NayaHttpResponse.internal_error") as fake_500:
            fake_smtp_class.side_effect = OSError("connection refused")

            # Si esto explota con AttributeError, el bug volvió.
            _run(EmailService.send_verification_email(
                to_name="x", to_email="x@y.com", verification_code="z"
            ))
        fake_500.assert_called_once()

    def test_generic_exception_caught(self):
        with patch("app.utils.email.smtplib.SMTP") as fake_smtp_class, \
             patch("app.utils.email.NayaHttpResponse.internal_error") as fake_500:
            instance = MagicMock()
            instance.sendmail.side_effect = ValueError("malformed message")
            fake_smtp_class.return_value = instance

            _run(EmailService.send_verification_email(
                to_name="x", to_email="x@y.com", verification_code="z"
            ))
        fake_500.assert_called_once()


class TestSendConnectionCodeEmailSuccess:
    def test_sendmail_invoked(self, patched_smtp):
        _, smtp_instance = patched_smtp
        _run(EmailService.send_conection_code_email(
            to_name="Mama", to_email="mama@naya.local", verification_code="42"
        ))
        smtp_instance.sendmail.assert_called_once()


class TestSendConnectionCodeEmailFailure:
    def test_smtp_failure_does_not_raise(self):
        with patch("app.utils.email.smtplib.SMTP") as fake_smtp_class, \
             patch("app.utils.email.NayaHttpResponse.internal_error") as fake_500:
            instance = MagicMock()
            instance.sendmail.side_effect = smtplib.SMTPRecipientsRefused({})
            fake_smtp_class.return_value = instance
            _run(EmailService.send_conection_code_email(
                to_name="x", to_email="x@y.com", verification_code="z"
            ))
        fake_500.assert_called_once()
