from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from library.views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html")),
    path("", include("library.urls")),
    path("api/health/", health),
]
