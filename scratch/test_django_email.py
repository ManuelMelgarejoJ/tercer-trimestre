import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steamlike_backend.settings')
django.setup()

from library.services.email_service import EmailService

try:
    print("Attempting to send email...")
    success = EmailService.send_email(
        to="manuel@example.com",
        subject="Test Django Email",
        text="This is a test from within Django environment."
    )
    print(f"Success: {success}")
except Exception as e:
    print(f"Error: {e}")
