from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    # When Vercel invokes api/index.py, it may pass path without /api prefix; accept both.
    path("", include("core.urls")),
]
