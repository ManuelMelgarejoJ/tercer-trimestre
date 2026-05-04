from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import LibraryEntry
from .helpers import validation_error, unauthorized, not_found, load_json
from .services.email_service import (
    EmailService,
    ExternalServiceError,
    ExternalServiceUnavailable,
)


ALLOWED_STATUS = {"wishlist", "playing", "completed", "dropped"}


def serialize_entry(entry):
    return {
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played,
    }


def get_user_entry_or_404(user, entry_id):
    try:
        return LibraryEntry.objects.get(id=entry_id, user=user)
    except LibraryEntry.DoesNotExist:
        return None


def validate_entry_payload(data, require_all_fields):
    required = ("external_game_id", "status", "hours_played")
    if require_all_fields and any(field not in data for field in required):
        return validation_error({"campos": "faltantes"})

    if "status" in data and data["status"] not in ALLOWED_STATUS:
        return validation_error({"status": "valor no permitido"})

    if "hours_played" in data:
        if not isinstance(data["hours_played"], int) or data["hours_played"] < 0:
            return validation_error({"hours_played": "debe ser >= 0"})

    return None


def external_service_unavailable():
    return JsonResponse({
        "error": "external_service_unavailable",
        "message": "Servicio externo no disponible"
    }, status=503)


def external_service_error():
    return JsonResponse({
        "error": "external_service_error",
        "message": "Error del servicio externo"
    }, status=502)


def validate_string_fields(data, fields):
    for field in fields:
        if field not in data:
            return validation_error({"campos": "faltantes"})
        if not isinstance(data[field], str):
            return validation_error({field: "debe ser string"})
    return None


def is_valid_email(email):
    return isinstance(email, str) and "@" in email and email.index("@") > 0 and not email.endswith("@")


# healthcheck
@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


# registro usuario
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    data, error_response = load_json(request)
    if error_response:
        return error_response

    validation_response = validate_string_fields(data, ("username", "password", "email"))
    if validation_response:
        return validation_response

    if not is_valid_email(data["email"]):
        return validation_error({"email": "formato invalido"})

    if len(data["password"]) < 8:
        return validation_error({"password": "mínimo 8 caracteres"})

    if User.objects.filter(username=data["username"]).exists():
        return validation_error({"username": "ya existe"})

    user = User.objects.create_user(
        username=data["username"],
        password=data["password"],
        email=data["email"],
    )

    email_sent = True

    try:
        EmailService.send_email(
            to=user.email,
            subject="Bienvenido a Steamlike",
            text=f"Hola {user.username}, tu cuenta se ha creado correctamente.",
            action="register_welcome",
            user=user,
        )
    except (ExternalServiceUnavailable, ExternalServiceError):
        email_sent = False

    response = {"id": user.id, "username": user.username, "email": user.email, "email_sent": email_sent}
    if not email_sent:
        response["warning"] = "Usuario creado, pero no se pudo enviar el correo de bienvenida"

    return JsonResponse(response, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def debug_email_test(request):
    if not settings.DEBUG:
        return JsonResponse({"error": "not_found", "message": "Ruta no disponible"}, status=404)

    data, error_response = load_json(request)
    if error_response:
        return error_response

    validation_response = validate_string_fields(data, ("to", "subject", "text"))
    if validation_response:
        return validation_response

    try:
        EmailService.send_email(
            to=data["to"],
            subject=data["subject"],
            text=data["text"],
            action="send_email",
        )
    except ExternalServiceUnavailable:
        return external_service_unavailable()
    except ExternalServiceError:
        return external_service_error()

    return JsonResponse({"ok": True}, status=200)


# login usuario
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    data, error_response = load_json(request)
    if error_response:
        return error_response

    if "username" not in data or "password" not in data:
        return validation_error({"campos": "faltantes"})

    user = authenticate(request, username=data["username"], password=data["password"])
    if user is None:
        return JsonResponse({"error": "unauthorized", "message": "Credenciales incorrectas"}, status=401)

    login(request, user)
    return JsonResponse({"id": user.id, "username": user.username}, status=200)


# logout usuario
@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({}, status=204)


# usuario actual
@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def users_me(request):
    if not request.user.is_authenticated:
        return unauthorized()

    if request.method == "DELETE":
        request.user.delete()
        return JsonResponse({}, status=204)

    return JsonResponse({"id": request.user.id, "username": request.user.username}, status=200)


# cambiar contraseña
@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    if not request.user.is_authenticated:
        return unauthorized()

    data, error_response = load_json(request)
    if error_response:
        return error_response

    if "current_password" not in data or "new_password" not in data:
        return validation_error({"campos": "faltantes"})

    if not request.user.check_password(data["current_password"]):
        return validation_error({"current_password": "incorrecta"})

    if len(data["new_password"]) < 8:
        return validation_error({"new_password": "mínimo 8 caracteres"})

    request.user.set_password(data["new_password"])
    request.user.save()

    return JsonResponse({"ok": True}, status=200)


# crear/listar entradas
@csrf_exempt
@require_http_methods(["GET", "POST"])
def library_entries(request):
    if not request.user.is_authenticated:
        return unauthorized()

    if request.method == "GET":
        entries = LibraryEntry.objects.filter(user=request.user)
        return JsonResponse([serialize_entry(entry) for entry in entries], safe=False, status=200)

    data, error_response = load_json(request)
    if error_response:
        return error_response

    validation_response = validate_entry_payload(data, require_all_fields=True)
    if validation_response:
        return validation_response

    entry = LibraryEntry.objects.create(
        external_game_id=data["external_game_id"],
        status=data["status"],
        hours_played=data["hours_played"],
        user=request.user
    )

    return JsonResponse(serialize_entry(entry), status=201)


# get + patch entrada
@csrf_exempt
@require_http_methods(["GET", "PATCH", "PUT"])
def library_entry_detail(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized()

    entry = get_user_entry_or_404(request.user, entry_id)
    if entry is None:
        return not_found()

    if request.method == "GET":
        return JsonResponse(serialize_entry(entry), status=200)

    data, error_response = load_json(request)
    if error_response:
        return error_response

    validation_response = validate_entry_payload(data, require_all_fields=request.method == "PUT")
    if validation_response:
        return validation_response

    if "external_game_id" in data:
        entry.external_game_id = data["external_game_id"]
    if "status" in data:
        entry.status = data["status"]
    if "hours_played" in data:
        entry.hours_played = data["hours_played"]

    entry.save()
    return JsonResponse(serialize_entry(entry), status=200)


# put entrada completa
@csrf_exempt
@require_http_methods(["PUT"])
def replace_library_entry(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized()

    entry = get_user_entry_or_404(request.user, entry_id)
    if entry is None:
        return not_found()

    data, error_response = load_json(request)
    if error_response:
        return error_response

    validation_response = validate_entry_payload(data, require_all_fields=True)
    if validation_response:
        return validation_response

    entry.external_game_id = data["external_game_id"]
    entry.status = data["status"]
    entry.hours_played = data["hours_played"]
    entry.save()

    return JsonResponse(serialize_entry(entry), status=200)


# delete entrada
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_library_entry(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized()

    entry = get_user_entry_or_404(request.user, entry_id)
    if entry is None:
        return not_found()

    entry.delete()
    return JsonResponse({}, status=204)

