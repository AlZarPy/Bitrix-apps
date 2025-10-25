from django.urls import path
from . import views

app_name = "qr_public"

urlpatterns = [
    path("<uuid:token>/", views.product_public_view, name="product_public"),
]
