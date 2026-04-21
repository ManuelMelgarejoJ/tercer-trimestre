import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import LibraryEntry
from .helpers import validation_error, unauthorized, not_found


ALLOWED_STATUS = {"wishlist", "playing", "completed", "dropped"}


# healthcheck
@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


# registro usuario
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    if "username" not in data or "password" not in data:
        return validation_error({"campos": "faltantes"})

    if len(data["password"]) < 8:
        return validation_error({"password": "mínimo 8 caracteres"})

    if User.objects.filter(username=data["username"]).exists():
        return validation_error({"username": "ya existe"})

    user = User.objects.create_user(username=data["username"], password=data["password"])

    return JsonResponse({"id": user.id, "username": user.username}, status=201)


# login usuario
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

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
@require_GET
def users_me(request):
    if not request.user.is_authenticated:
        return unauthorized()

    return JsonResponse({"id": request.user.id, "username": request.user.username}, status=200)


# cambiar contraseña
@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    if not request.user.is_authenticated:
        return unauthorized()

    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    if "current_password" not in data or "new_password" not in data:
        return validation_error({"campos": "faltantes"})

    if not request.user.check_password(data["current_password"]):
        return validation_error({"current_password": "incorrecta"})

    if len(data["new_password"]) < 8:
        return validation_error({"new_password": "mínimo 8 caracteres"})

    request.user.set_password(data["new_password"])
    request.user.save()

    return JsonResponse({"ok": True}, status=200)


# crear entrada
@csrf_exempt
@require_http_methods(["POST"])
def create_library_entry(request):
    if not request.user.is_authenticated:
        return unauthorized()

    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    required = ("external_game_id", "status", "hours_played")
    if any(f not in data for f in required):
        return validation_error({"campos": "faltantes"})

    if data["status"] not in ALLOWED_STATUS:
        return validation_error({"status": "valor no permitido"})

    entry = LibraryEntry.objects.create(
        external_game_id=data["external_game_id"],
        status=data["status"],
        hours_played=data["hours_played"],
        user=request.user
    )

    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played
    }, status=201)


# listar entradas
@require_GET
def list_library_entries(request):
    if not request.user.is_authenticated:
        return unauthorized()

    entries = LibraryEntry.objects.filter(user=request.user)

    return JsonResponse([
        {
            "id": e.id,
            "external_game_id": e.external_game_id,
            "status": e.status,
            "hours_played": e.hours_played
        }
        for e in entries
    ], safe=False, status=200)


# get + patch entrada
@csrf_exempt
@require_http_methods(["GET", "PATCH"])
def get_library_entries(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized()

    try:
        entry = LibraryEntry.objects.get(id=entry_id, user=request.user)
    except LibraryEntry.DoesNotExist:
        return not_found()

    if request.method == "GET":
        return JsonResponse({
            "id": entry.id,
            "external_game_id": entry.external_game_id,
            "status": entry.status,
            "hours_played": entry.hours_played
        }, status=200)

    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    if "status" in data:
        if data["status"] not in ALLOWED_STATUS:
            return validation_error({"status": "valor no permitido"})
        entry.status = data["status"]

    if "hours_played" in data:
        if not isinstance(data["hours_played"], int) or data["hours_played"] < 0:
            return validation_error({"hours_played": "debe ser >= 0"})
        entry.hours_played = data["hours_played"]

    entry.save()

    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played
    }, status=200)


# put entrada completa
@csrf_exempt
@require_http_methods(["PUT"])
def put_library_entry(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized()

    try:
        entry = LibraryEntry.objects.get(id=entry_id, user=request.user)
    except LibraryEntry.DoesNotExist:
        return not_found()

    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    required = ("external_game_id", "status", "hours_played")
    if any(f not in data for f in required):
        return validation_error({"campos": "faltantes"})

    if data["status"] not in ALLOWED_STATUS:
        return validation_error({"status": "valor no permitido"})

    entry.external_game_id = data["external_game_id"]
    entry.status = data["status"]
    entry.hours_played = data["hours_played"]
    entry.save()

    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played
    }, status=200)


# borrar entrada
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_library_entry(request, entry_id):
    if not request.user.is_authenticated:
        return unauthorized()

    try:
        entry = LibraryEntry.objects.get(id=entry_id, user=request.user)
    except LibraryEntry.DoesNotExist:
        return not_found()

    entry.delete()
    return JsonResponse({}, status=204)


# borrar usuario
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request):
    if not request.user.is_authenticated:
        return unauthorized()

    request.user.delete()
    return JsonResponse({}, status=204)
