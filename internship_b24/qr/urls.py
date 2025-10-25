from django.urls import path
from . import views

app_name = "qr"

urlpatterns = [
    path("", views.qr_form_view, name="qr_form"),
    path("success/<uuid:token>/", views.qr_success_view, name="qr_success"),
    path("api/product-search", views.api_product_search, name="api_product_search"),
]
