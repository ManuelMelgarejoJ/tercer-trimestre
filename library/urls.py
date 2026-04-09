from django.urls import path
from .views import health, create_library_entry

urlpatterns = [
    path("health/", health),
    path("api/library/entries/", create_library_entry),
]
