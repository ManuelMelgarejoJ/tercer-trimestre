import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import LibraryEntry


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


ALLOWED_STATUS = {"wishlist", "playing", "completed", "dropped"}


def validation_error(details=None):
    return JsonResponse({
        "error": "validation_error",
        "message": "Datos de entrada inválidos",
        "details": details or {}
    }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def create_library_entry(request):
    # validar JSON
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

    # validar tipos
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

    if LibraryEntry.objects.filter(external_game_id=external_game_id).exists():
        return JsonResponse({
            "error": "duplicate_entry",
            "message": "La entrada ya existe"
        }, status=409)

    entry = LibraryEntry.objects.create(
        external_game_id=external_game_id,
        status=status,
        hours_played=hours_played,
    )

    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played,
    }, status=201)


@require_GET
def list_library_entries(request):
    # listar entradas
    entries = LibraryEntry.objects.all()
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


@csrf_exempt
@require_http_methods(["GET", "PATCH"])
def get_library_entries(request, entry_id):
    # obtener entrada
    try:
        entry = LibraryEntry.objects.get(id=entry_id)
    except LibraryEntry.DoesNotExist:
        return JsonResponse({
            "error": "not_found",
            "message": "La entrada no existe"
        }, status=404)

    if request.method == "GET":
        return JsonResponse({
            "id": entry.id,
            "external_game_id": entry.external_game_id,
            "status": entry.status,
            "hours_played": entry.hours_played,
        }, status=200)

    # actualizar entrada
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


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_library_entry(request, entry_id):
    # borrar entrada
    try:
        entry = LibraryEntry.objects.get(id=entry_id)
    except LibraryEntry.DoesNotExist:
        return JsonResponse({
            "error": "not_found",
            "message": "La entrada no existe"
        }, status=404)

    entry.delete()

    return JsonResponse({
        "status": "deleted",
        "id": entry_id
    }, status=200)
