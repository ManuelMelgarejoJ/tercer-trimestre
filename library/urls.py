from django.urls import path
from .views import (
    health,
    register,
    debug_email_test,
    login_view,
    logout_view,
    users_me,
    change_password,
    library_entries,
    library_entry_detail,
    replace_library_entry,
    delete_library_entry,
)

urlpatterns = [
    path("health/", health),
    path("api/auth/register/", register),
    path("api/debug/email/test/", debug_email_test),
    path("api/auth/login/", login_view),
    path("api/auth/logout/", logout_view),
    path("api/users/me/", users_me),
    path("api/users/me/password/", change_password),
    path("api/library/entries/", library_entries),
    path("api/library/entries/<int:entry_id>/", library_entry_detail),
    path("api/library/entries/<int:entry_id>/put/", replace_library_entry),
    path("api/library/entries/<int:entry_id>/delete/", delete_library_entry),
]
