from django.urls import path
from .views import (
    health,
    register,
    login_view,
    users_me,
    create_library_entry,
    list_library_entries,
    get_library_entries,
    delete_library_entry
)

urlpatterns = [
    path("health/", health),
    path("api/auth/register/", register),
    path("api/auth/login/", login_view),
    path("api/users/me/", users_me),
    path("api/library/entries/", create_library_entry),
    path("api/library/entries/list/", list_library_entries),
    path("api/library/entries/<int:entry_id>/", get_library_entries),
    path("api/library/entries/<int:entry_id>/delete/", delete_library_entry),
]
