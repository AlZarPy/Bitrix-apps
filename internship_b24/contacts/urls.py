from django.urls import path
from . import views

app_name = "contacts"

urlpatterns = [
    path("import/", views.import_view, name="import"),
    path("export/", views.export_view, name="export"),
]
