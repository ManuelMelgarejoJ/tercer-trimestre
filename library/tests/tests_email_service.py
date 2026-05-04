from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase, override_settings

from library.services.email_service import (
    EmailService,
    ExternalServiceError,
    ExternalServiceUnavailable,
)


@override_settings(
    MAILEROO_ENDPOINT="https://smtp.maileroo.test/api/v2/emails",
    MAILEROO_TOKEN="token-test",
    MAILEROO_FROM="from@example.com",
)
class EmailServiceTests(SimpleTestCase):
    @patch("library.services.email_service.requests.post")
    def test_send_email_ok(self, post):
        response = Mock(status_code=200)
        response.json.return_value = {"success": True}
        post.return_value = response

        result = EmailService.send_email("to@example.com", "Subject", "Text")

        self.assertTrue(result)
        post.assert_called_once()
        _, kwargs = post.call_args
        self.assertEqual(kwargs["json"]["to"], [{"address": "to@example.com"}])
        self.assertEqual(kwargs["json"]["from"], {"address": "from@example.com"})
        self.assertEqual(kwargs["json"]["plain"], "Text")
        self.assertNotIn("token-test", str(kwargs["json"]))

    @patch("library.services.email_service.requests.post", side_effect=requests.exceptions.Timeout)
    def test_send_email_timeout_raises_503_error(self, post):
        with self.assertRaises(ExternalServiceUnavailable):
            EmailService.send_email("to@example.com", "Subject", "Text")

    @patch("library.services.email_service.requests.post", side_effect=requests.exceptions.ConnectionError)
    def test_send_email_connection_error_raises_503_error(self, post):
        with self.assertRaises(ExternalServiceUnavailable):
            EmailService.send_email("to@example.com", "Subject", "Text")

    @patch("library.services.email_service.requests.post")
    def test_send_email_provider_status_error_raises_502_error(self, post):
        response = Mock(status_code=401)
        response.json.return_value = {"success": False}
        post.return_value = response

        with self.assertRaises(ExternalServiceError):
            EmailService.send_email("to@example.com", "Subject", "Text")

    @patch("library.services.email_service.requests.post")
    def test_send_email_invalid_response_raises_502_error(self, post):
        response = Mock(status_code=200)
        response.json.side_effect = ValueError
        post.return_value = response

        with self.assertRaises(ExternalServiceError):
            EmailService.send_email("to@example.com", "Subject", "Text")
