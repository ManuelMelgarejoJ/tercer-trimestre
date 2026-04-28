from django.contrib import admin
from django.urls import path
from library.views import (
    health,
    register,
    login_view,
    logout_view,
    users_me,
    change_password,
    create_library_entry,
    list_library_entries,
    get_library_entry,
    update_library_entry,
    delete_library_entry,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # health
    path("api/health/", health),

    # auth
    path("api/auth/register/", register),
    path("api/auth/login/", login_view),
    path("api/auth/logout/", logout_view),

    # user info + password
    path("api/users/me/", users_me),
    path("api/users/me/password/", change_password),

    # library entries
    path("api/library/entries/", create_library_entry),
    path("api/library/entries/list/", list_library_entries),
    path("api/library/entries/<int:entry_id>/", get_library_entry),
    path("api/library/entries/<int:entry_id>/update/", update_library_entry),
    path("api/library/entries/<int:entry_id>/delete/", delete_library_entry),
]
