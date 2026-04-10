import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import LibraryEntry

# HEALTH CHECK
@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


# CONSTANTES
ALLOWED_STATUS = {"wishlist", "playing", "completed", "dropped"}


# FORMATO ESTÁNDAR DE ERRORES
def validation_error(details=None):
    return JsonResponse({
        "error": "validation_error",
        "message": "Datos de entrada inválidos",
        "details": details or {}
    }, status=400)


# -----------------------------
# POST → CREAR ENTRADA
# -----------------------------
@csrf_exempt
@require_http_methods(["POST"])
def create_library_entry(request):
    # 1. Intentar leer el JSON
    try:
        data = json.loads(request.body)
    except:
        return validation_error({"json": "malformado"})

    # 2. JSON no vacío
    if not isinstance(data, dict) or data == {}:
        return validation_error({"json": "vacío"})

    # 3. Comprobar campos obligatorios
    required = ("external_game_id", "status", "hours_played")
    missing = [f for f in required if f not in data]
    if missing:
        return validation_error({field: "faltante" for field in missing})

    external_game_id = data["external_game_id"]
    status = data["status"]
    hours_played = data["hours_played"]

    # 4. Tipos correctos
    if not isinstance(external_game_id, str):
        return validation_error({"external_game_id": "debe ser string"})

    if not isinstance(status, str):
        return validation_error({"status": "debe ser string"})

    if not isinstance(hours_played, int):
        return validation_error({"hours_played": "debe ser integer"})

    # 5. Dominios correctos
    if status not in ALLOWED_STATUS:
        return validation_error({"status": "valor no permitido"})

    if hours_played < 0:
        return validation_error({"hours_played": "debe ser >= 0"})

    # 6. Comprobar duplicados
    if LibraryEntry.objects.filter(external_game_id=external_game_id).exists():
        return JsonResponse({
            "error": "duplicate_entry",
            "message": "La entrada ya existe"
        }, status=409)

    # 7. Crear la entrada
    entry = LibraryEntry.objects.create(
        external_game_id=external_game_id,
        status=status,
        hours_played=hours_played,
    )

    # 8. Respuesta correcta
    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played,
    }, status=201)

# GET → LISTADO DE ENTRADAS
@require_GET
def list_library_entries(request):
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


# GET → DETALLE POR ID
@require_GET
def get_library_entry(request, entry_id):
    try:
        entry = LibraryEntry.objects.get(id=entry_id)
    except LibraryEntry.DoesNotExist:
        return JsonResponse({
            "error": "not_found",
            "message": "La entrada no existe"
        }, status=404)

    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played,
    }, status=200)
