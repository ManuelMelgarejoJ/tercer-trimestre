import os
import django
import json
from django.conf import settings
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'steamlike_backend.settings')
django.setup()

client = Client()

payload = {
    "username": "testuser_real_email_3",
    "password": "password123",
    "email": "manuel@example.com"
}

print(f"Attempting to register user: {payload['username']}")
response = client.post(
    "/api/auth/register/",
    data=json.dumps(payload),
    content_type="application/json"
)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.json()}")

if response.status_code == 201:
    print("User created successfully.")
    if response.json().get("email_sent"):
        print("Email reported as SENT.")
    else:
        print("Email reported as NOT SENT.")
        if "warning" in response.json():
            print(f"Warning: {response.json()['warning']}")
else:
    print("Registration failed.")
