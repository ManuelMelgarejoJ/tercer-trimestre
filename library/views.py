from django.http import JsonResponse

def method_not_allowed():
    return JsonResponse({"error": "method_not_allowed"}, status=405)

def health(request):
    if request.method != "GET":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

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

def users_me(request):
    if request.method != "GET":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

def change_password(request):
    if request.method != "POST":
        return method_not_allowed()
    return JsonResponse({"status": "ok"})

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
