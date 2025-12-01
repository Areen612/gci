"""URL configuration for the GCI project."""
from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)