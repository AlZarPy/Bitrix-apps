from django.urls import path
from .views import employees_list_view, generate_calls_view

app_name = "employees"

urlpatterns = [
    path("", employees_list_view, name="list"),
    path("generate-calls/", generate_calls_view, name="generate_calls"),
]
