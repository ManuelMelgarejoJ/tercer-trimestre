import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from library.models import LibraryEntry
from library.validators import (
    validate_create_payload,
    validate_put_payload,
    validate_patch_payload,
    validate_login_payload,
    validate_password_change_payload,
)

# -------------------------
# Helper para métodos no permitidos
# -------------------------

def method_not_allowed():
    return JsonResponse({"error": "method_not_allowed"}, status=405)

# -------------------------
# HEALTH
# -------------------------

def health(request):
    if request.method != "GET":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

# -------------------------
# AUTH
# -------------------------

def register(request):
    if request.method != "POST":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def login_view(request):
    if request.method != "POST":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def logout_view(request):
    if request.method != "POST":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

# -------------------------
# USERS / ME
# -------------------------

def users_me(request):
    if request.method != "GET":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def change_password(request):
    if request.method != "POST":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

# -------------------------
# LIBRARY ENTRIES
# -------------------------

def create_library_entry(request):
    if request.method != "POST":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def list_library_entries(request):
    if request.method != "GET":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def get_library_entry(request, entry_id):
    if request.method != "GET":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def update_library_entry(request, entry_id):
    if request.method not in ["PUT", "PATCH"]:
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def delete_library_entry(request, entry_id):
    if request.method != "DELETE":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})
