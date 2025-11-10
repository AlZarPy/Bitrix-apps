from django.urls import path
from . import views

app_name = "map"

urlpatterns = [
    path("", views.companies_map_view, name="companies_map"),
]
