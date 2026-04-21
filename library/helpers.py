import json
from django.http import JsonResponse

# error 400
def validation_error(details=None):
    return JsonResponse({
        "error": "validation_error",
        "message": "Datos de entrada inválidos",
        "details": details or {}
    }, status=400)

# error 401
def unauthorized(message="No autenticado"):
    return JsonResponse({
        "error": "unauthorized",
        "message": message
    }, status=401)

# error 404
def not_found():
    return JsonResponse({
        "error": "not_found",
        "message": "La entrada solicitada no existe"
    }, status=404)

# cargar JSON
def load_json(request):
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict) or data == {}:
            return None, validation_error({"json": "vacío"})
        return data, None
    except:
        return None, validation_error({"json": "malformado"})
