import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from .models import LibraryEntry

# Vista health para evitar el error de importación
@require_GET
def health(request):
    return JsonResponse({"status": "ok"})

ALLOWED_STATUS = {"wishlist", "playing", "completed", "dropped"}

@require_http_methods(["POST"])
def create_library_entry(request):
    # 1. Intentar leer el JSON
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    # 2. JSON no vacío
    if not isinstance(data, dict) or data == {}:
        return JsonResponse({"error": "JSON vacío"}, status=400)

    # 3. Comprobar campos obligatorios
    required = ("external_game_id", "status", "hours_played")
    if not all(key in data for key in required):
        return JsonResponse({"error": "Faltan campos"}, status=400)

    external_game_id = data["external_game_id"]
    status = data["status"]
    hours_played = data["hours_played"]

    # 4. Tipos correctos
    if not isinstance(external_game_id, str):
        return JsonResponse({"error": "external_game_id debe ser string"}, status=400)

    if not isinstance(status, str):
        return JsonResponse({"error": "status debe ser string"}, status=400)

    if not isinstance(hours_played, int):
        return JsonResponse({"error": "hours_played debe ser integer"}, status=400)

    # 5. Dominios correctos
    if status not in ALLOWED_STATUS:
        return JsonResponse({"error": "status no permitido"}, status=400)

    if hours_played < 0:
        return JsonResponse({"error": "hours_played debe ser >= 0"}, status=400)

    # 6. Crear la entrada
    entry = LibraryEntry.objects.create(
        external_game_id=external_game_id,
        status=status,
        hours_played=hours_played,
    )

    # 7. Respuesta correcta
    return JsonResponse({
        "id": entry.id,
        "external_game_id": entry.external_game_id,
        "status": entry.status,
        "hours_played": entry.hours_played,
    }, status=201)

def validation_error(details=None):
    return JsonResponse({
        "error": "validation_error",
        "message": "Datos de entrada no validos",
        "details": details or {}
    }, status=400)