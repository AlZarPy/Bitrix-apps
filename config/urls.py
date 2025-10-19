from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("internship_b24.urls", namespace="internship_b24")),
]
