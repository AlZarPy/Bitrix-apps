from django.urls import path
from . import views

app_name = "internship_b24"

urlpatterns = [
    path("", views.index, name="index"),
    path("module1/", views.module1, name="module1"),
    path("module2/", views.module2, name="module2"),
    path("module3/", views.module3, name="module3"),
    path("module4/", views.module4, name="module4"),
    path("module5/", views.module5, name="module5"),
    path("oauth/bitrix/", views.oauth_bitrix, name="oauth_bitrix"),
]
