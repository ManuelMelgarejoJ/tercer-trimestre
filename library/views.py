import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import LibraryEntry


ALLOWED_STATUS = {"wishlist", "playing", "completed", "dropped"}


def validation_error(details=None):
    return JsonResponse({
        "error": "validation_error",
        "message": "Datos de entrada inválidos",
        "details": details or {}
    }, status=400)


def unauthorized(message):
    return JsonResponse({
        "error": "unauthorized",
        "message": message
    }, status=401)


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


# registro
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    if not isinstance(data, dict) or data == {}:
        return validation_error({"json": "vacío"})

    if "username" not in data or "password" not in data:
        return validation_error({"campos": "faltantes"})

    username = data["username"]
    password = data["password"]

    if not isinstance(username, str):
        return validation_error({"username": "debe ser string"})
    if not isinstance(password, str):
        return validation_error({"password": "debe ser string"})
    if len(password) < 8:
        return validation_error({"password": "mínimo 8 caracteres"})
    if User.objects.filter(username=username).exists():
        return validation_error({"username": "ya existe"})

    user = User.objects.create_user(username=username, password=password)

    return JsonResponse({
        "id": user.id,
        "username": user.username
    }, status=201)


# login
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    if "username" not in data or "password" not in data:
        return validation_error({"campos": "faltantes"})

    username = data["username"]
    password = data["password"]

    if not isinstance(username, str) or not isinstance(password, str):
        return validation_error({"tipos": "incorrectos"})

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({
            "error": "unauthorized",
            "message": "Credenciales incorrectas"
        }, status=401)

    login(request, user)

    return JsonResponse({
        "id": user.id,
        "username": user.username
    }, status=200)


# usuario actual
@require_GET
def users_me(request):
    if not request.user.is_authenticated:
        return unauthorized("No autenticado")

    return JsonResponse({
        "id": request.user.id,
        "username": request.user.username
    }, status=200)


# crear entrada
@csrf_exempt
@require_http_methods(["POST"])
def create_library_entry(request):
    if not request.user.is_authenticated:
        return unauthorized("No autenticado")

    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    if not isinstance(data, dict) or data == {}:
        return validation_error({"json": "vacío"})

    required = ("external_game_id", "status", "hours_played")
    missing = [f for f in required if f not in data]
    if missing:
        return validation_error({field: "faltante" for field in missing})

    external_game_id = data["external_game_id"]
    status = data["status"]
    hours_played = data["hours_played"]

    if not isinstance(external_game_id, str):
        return validation_error({"external_game_id": "debe ser string"})
    if not isinstance(status, str):
        return validation_error({"status": "debe ser string"})
    if not isinstance(hours_played, int):
        return validation_error({"hours_played": "debe ser integer"})
    if status not in ALLOWED_STATUS:
        return validation_error({"status": "valor no permitido"})
    if hours_played < 0:
        return validation_error({"hours_played": "debe ser >= 0"})

    entry = LibraryEntry.objects.create(
        external_game_id=external_game_id,
        status=status,
        hours_played=hours_played,
        user=request.user
    )

    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played,
    }, status=201)


# listar entradas
@require_GET
def list_library_entries(request):
    if not request.user.is_authenticated:
        return unauthorized("No autenticado")

    entries = LibraryEntry.objects.filter(user=request.user)

    data = [
        {
            "id": entry.id,
            "external_game_id": entry.external_game_id,
            "status": entry.status,
            "hours_played": entry.hours_played,
        }
        for entry in entries
    ]
    return JsonResponse(data, safe=False, status=200)


# get + patch entrada
@csrf_exempt
@require_http_methods(["GET", "PATCH"])
def get_library_entries(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized("No autenticado")

    try:
        entry = LibraryEntry.objects.get(id=entry_id, user=request.user)
    except LibraryEntry.DoesNotExist:
        return JsonResponse({
            "error": "not_found",
            "message": "La entrada solicitada no existe"
        }, status=404)

    if request.method == "GET":
        return JsonResponse({
            "id": entry.id,
            "external_game_id": entry.external_game_id,
            "status": entry.status,
            "hours_played": entry.hours_played,
        }, status=200)

    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    if not isinstance(data, dict) or data == {}:
        return validation_error({"json": "vacío"})

    allowed_fields = {"status", "hours_played"}
    unknown_fields = [f for f in data.keys() if f not in allowed_fields]

    if unknown_fields:
        return validation_error({"campos_desconocidos": unknown_fields})

    if "status" in data:
        if not isinstance(data["status"], str):
            return validation_error({"status": "debe ser string"})
        if data["status"] not in ALLOWED_STATUS:
            return validation_error({"status": "valor no permitido"})

    if "hours_played" in data:
        if not isinstance(data["hours_played"], int):
            return validation_error({"hours_played": "debe ser integer"})
        if data["hours_played"] < 0:
            return validation_error({"hours_played": "debe ser >= 0"})

    if "status" in data:
        entry.status = data["status"]

    if "hours_played" in data:
        entry.hours_played = data["hours_played"]

    entry.save()

    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played,
    }, status=200)


# borrar entrada
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_library_entry(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized("No autenticado")

    try:
        entry = LibraryEntry.objects.get(id=entry_id, user=request.user)
    except LibraryEntry.DoesNotExist:
        return JsonResponse({
            "error": "not_found",
            "message": "La entrada solicitada no existe"
        }, status=404)

    entry.delete()

    return JsonResponse({
        "status": "deleted",
        "id": entry_id
    }, status=200)
