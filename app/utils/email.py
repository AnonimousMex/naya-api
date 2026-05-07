import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.logger import logger
from app.core.settings import settings

from app.core.http_response import NayaHttpResponse

from app.constants.email_template import new_user_verification_code_email_tempalte


_EVT_EMAIL_SENT = "email.sent"
_EVT_EMAIL_SMTP_FAILED = "email.smtp_failed"
_EVT_EMAIL_SEND_FAILED = "email.send_failed"


def _email_domain(email: str) -> str:
    return email.split("@", 1)[1] if "@" in email else "<no-domain>"


class EmailService:
    @staticmethod
    async def send_verification_email(
        to_name: str, to_email: str, verification_code: str
    ):
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        smtp_username = settings.SMTP_USERNAME
        smtp_password = settings.SMTP_PASSWORD
        verification_code = verification_code

        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_username
        msg["To"] = to_email
        msg["Subject"] = "¡Verifica tu cuenta!"

        text = """¡Activa tu cuenta ahora!"""

        html = new_user_verification_code_email_tempalte(
            user_name=to_name, code=verification_code
        )

        mail = None
        try:
            first_part = MIMEText(text, "plain")
            second_part = MIMEText(html, "html")

            msg.attach(first_part)
            msg.attach(second_part)

            mail = smtplib.SMTP(smtp_server, smtp_port)

            mail.ehlo()

            mail.starttls()

            mail.login(smtp_username, smtp_password)
            mail.sendmail(smtp_username, to_email, msg.as_string())
            logger.info(
                _EVT_EMAIL_SENT,
                extra={
                    "event": _EVT_EMAIL_SENT,
                    "kind": "verification",
                    "to_domain": _email_domain(to_email),
                    "smtp_server": smtp_server,
                },
            )

        except smtplib.SMTPException as e:
            logger.error(
                _EVT_EMAIL_SMTP_FAILED,
                extra={
                    "event": _EVT_EMAIL_SMTP_FAILED,
                    "kind": "verification",
                    "to_domain": _email_domain(to_email),
                    "smtp_server": smtp_server,
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            NayaHttpResponse.internal_error()

        except Exception as e:
            logger.exception(
                _EVT_EMAIL_SEND_FAILED,
                extra={
                    "event": _EVT_EMAIL_SEND_FAILED,
                    "kind": "verification",
                    "to_domain": _email_domain(to_email),
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()

        finally:
            if mail is not None:
                try:
                    mail.quit()
                except Exception:  # noqa: BLE001 - best-effort cleanup
                    pass

    @staticmethod
    async def send_conection_code_email(
        to_name: str, to_email: str, verification_code: str
    ):
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        smtp_username = settings.SMTP_USERNAME
        smtp_password = settings.SMTP_PASSWORD
        verification_code = verification_code

        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_username
        msg["To"] = to_email
        msg["Subject"] = "¡Este es tu numero de conexión!"

        text = """¡Tu numero de Conexión!"""

        html = new_user_verification_code_email_tempalte(
            user_name=to_name, code=verification_code
        )

        mail = None
        try:
            first_part = MIMEText(text, "plain")
            second_part = MIMEText(html, "html")

            msg.attach(first_part)
            msg.attach(second_part)

            mail = smtplib.SMTP(smtp_server, smtp_port)

            mail.ehlo()

            mail.starttls()

            mail.login(smtp_username, smtp_password)
            mail.sendmail(smtp_username, to_email, msg.as_string())
            logger.info(
                _EVT_EMAIL_SENT,
                extra={
                    "event": _EVT_EMAIL_SENT,
                    "kind": "connection_code",
                    "to_domain": _email_domain(to_email),
                    "smtp_server": smtp_server,
                },
            )

        except smtplib.SMTPException as e:
            logger.error(
                _EVT_EMAIL_SMTP_FAILED,
                extra={
                    "event": _EVT_EMAIL_SMTP_FAILED,
                    "kind": "connection_code",
                    "to_domain": _email_domain(to_email),
                    "smtp_server": smtp_server,
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            NayaHttpResponse.internal_error()

        except Exception as e:
            logger.exception(
                _EVT_EMAIL_SEND_FAILED,
                extra={
                    "event": _EVT_EMAIL_SEND_FAILED,
                    "kind": "connection_code",
                    "to_domain": _email_domain(to_email),
                    "error_class": e.__class__.__name__,
                    "error": str(e),
                },
            )
            NayaHttpResponse.internal_error()

        finally:
            if mail is not None:
                try:
                    mail.quit()
                except Exception:  # noqa: BLE001 - best-effort cleanup
                    pass
