import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steamlike_backend.settings')
django.setup()

from library.services.email_service import EmailService

try:
    print("Attempting to send email to invalid address...")
    # This should probably return an error from Maileroo if the address format is invalid or rejected
    success = EmailService.send_email(
        to="not-an-email",
        subject="Test Invalid Email",
        text="This should fail."
    )
    print(f"Success: {success}")
except Exception as e:
    print(f"Error type: {type(e)}")
    print(f"Error: {e}")
