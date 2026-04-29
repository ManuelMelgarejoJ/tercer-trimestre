import requests
from django.conf import settings

class ExternalServiceUnavailable(Exception):
    """503 - No hay respuesta del proveedor (timeout/red)."""
    pass

class ExternalServiceError(Exception):
    """502 - El proveedor respondió con error o datos inválidos."""
    pass


class EmailService:

    @staticmethod
    def send_email(to, subject, text, html=None):
        """
        Envía un email usando Maileroo.
        Traduce fallos externos a errores controlados.
        """

        endpoint = getattr(settings, "MAILEROO_ENDPOINT", None)
        token = getattr(settings, "MAILEROO_TOKEN", None)
        from_address = getattr(settings, "MAILEROO_FROM", None)

        payload = {
            "from": from_address,
            "to": to,
            "subject": subject,
            "text": text,
        }

        if html:
            payload["html"] = html

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=5
            )

        except requests.exceptions.Timeout:
            raise ExternalServiceUnavailable()

        except requests.exceptions.RequestException:
            raise ExternalServiceUnavailable()

        # Si Maileroo responde con error
        if response.status_code >= 500:
            raise ExternalServiceUnavailable()

        if response.status_code >= 400:
            raise ExternalServiceError()

        # Si la respuesta no es JSON válido
        try:
            data = response.json()
        except ValueError:
            raise ExternalServiceError()

        # Si Maileroo indica fallo
        if not data.get("success", False):
            raise ExternalServiceError()

        return True
