from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse


def kok(_request):
    return JsonResponse({
        "servis": "AKS - Alternatif Kapasite Skoru API (Django)",
        "api": "/api/",
        "admin": "/admin/",
        "docs": "/api/bilgi",
    })


urlpatterns = [
    path("", kok),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]
