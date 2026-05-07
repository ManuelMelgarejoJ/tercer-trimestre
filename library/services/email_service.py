import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ExternalServiceUnavailable(Exception):
    """503 - No hay respuesta del proveedor (timeout/red)."""


class ExternalServiceError(Exception):
    """502 - El proveedor respondio con error o datos invalidos."""


class EmailService:
    @staticmethod
    def send_email(to, subject, text, html=None, action="send_email", user=None):
        """
        Envia un email usando Maileroo.
        Traduce fallos externos a errores controlados.
        """
        endpoint = getattr(settings, "MAILEROO_ENDPOINT", None)
        token = getattr(settings, "MAILEROO_TOKEN", None)
        from_address = getattr(settings, "MAILEROO_FROM", None)

        log_context = {
            "action": action,
            "user": EmailService._serialize_user(user),
            "to": to,
        }
        logger.info(
            "intento de envio de email %s",
            EmailService._format_context({**log_context, "result": "attempt"}),
        )

        if not endpoint or not token or not from_address:
            logger.error(
                "fallo por configuracion del proveedor de email %s",
                EmailService._format_context({
                    **log_context,
                    "result": "error",
                    "error_type": "provider_config",
                }),
            )
            raise ExternalServiceError()

        payload = {
            "from": {
                "address": from_address,
                "name": "Steamlike"
            },
            "to": [
                {
                    "address": to,
                    "name": to.split("@")[0]
                }
            ],
            "subject": subject,
            "plain": text,
        }

        if html:
            payload["html"] = html

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=5)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            logger.warning(
                "fallo por timeout/red en email %s",
                EmailService._format_context({
                    **log_context,
                    "result": "error",
                    "error_type": "external_service_unavailable",
                    "exception": exc.__class__.__name__,
                }),
            )
            raise ExternalServiceUnavailable()
        except requests.exceptions.RequestException as exc:
            logger.warning(
                "fallo por error de red en email %s",
                EmailService._format_context({
                    **log_context,
                    "result": "error",
                    "error_type": "external_service_unavailable",
                    "exception": exc.__class__.__name__,
                }),
            )
            raise ExternalServiceUnavailable()

        if response.status_code >= 400:
            logger.warning(
                "fallo por respuesta del proveedor de email %s",
                EmailService._format_context({
                    **log_context,
                    "result": "error",
                    "error_type": "external_service_error",
                    "status_code": response.status_code,
                    "response": response.text[:500],
                }),
            )
            raise ExternalServiceError()

        try:
            data = response.json()
        except ValueError:
            logger.warning(
                "fallo por respuesta invalida del proveedor de email %s",
                EmailService._format_context({
                    **log_context,
                    "result": "error",
                    "error_type": "external_service_error",
                    "status_code": response.status_code,
                }),
            )
            raise ExternalServiceError()

        if not data.get("success", False):
            logger.warning(
                "fallo indicado por el proveedor de email %s",
                EmailService._format_context({
                    **log_context,
                    "result": "error",
                    "error_type": "external_service_error",
                    "status_code": response.status_code,
                    "response": str(data)[:300],
                }),
            )
            raise ExternalServiceError()

        logger.info(
            "envio OK %s",
            EmailService._format_context({**log_context, "result": "ok"}),
        )
        return True

    @staticmethod
    def _serialize_user(user):
        if user is None:
            return None
        return {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
        }

    @staticmethod
    def _format_context(context):
        return " ".join(f"{key}={value}" for key, value in context.items() if value is not None)
