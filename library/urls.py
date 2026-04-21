from django.urls import path
from .views import (
    health,
    register,
    login_view,
    logout_view,
    users_me,
    change_password,
    create_library_entry,
    list_library_entries,
    get_library_entries,
    put_library_entry,
    delete_library_entry,
    delete_user
)

urlpatterns = [
    path("health/", health),
    path("api/auth/register/", register),
    path("api/auth/login/", login_view),
    path("api/auth/logout/", logout_view),
    path("api/users/me/", users_me),
    path("api/users/me/password/", change_password),
    path("api/users/me/delete/", delete_user),
    path("api/library/entries/", create_library_entry),
    path("api/library/entries/list/", list_library_entries),
    path("api/library/entries/<int:entry_id>/", get_library_entries),
    path("api/library/entries/<int:entry_id>/put/", put_library_entry),
    path("api/library/entries/<int:entry_id>/delete/", delete_library_entry),
]
