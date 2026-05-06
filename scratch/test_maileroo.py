import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")

token = os.getenv("MAILEROO_TOKEN")
from_address = os.getenv("MAILEROO_FROM")
endpoint = os.getenv("MAILEROO_ENDPOINT")

print(f"Token: {token[:5]}...")
print(f"From: {from_address}")
print(f"Endpoint: {endpoint}")

payload = {
    "from": {"address": from_address},
    "to": [{"address": "manuel@example.com"}], # Replace with a test email if needed, but we just want to see the API response
    "subject": "Test Email",
    "plain": "This is a test email.",
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

try:
    response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
