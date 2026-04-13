from django.urls import path
from .views import (health,create_library_entry,list_library_entries,get_library_entry,delete_library_entry)

urlpatterns = [
    path("health/", health),
    path("api/library/entries/", create_library_entry),
    path("api/library/entries/list/", list_library_entries),
    path("api/library/entries/<int:entry_id>/", get_library_entry),
    path("api/library/entries/<int:entry_id>/delete/", delete_library_entry),

]
