from django.urls import path, include
from . import views
from internship_b24.qr import views as qr_views

app_name = "internship_b24"

urlpatterns = [
    path("", views.index, name="index"),

    path("deals/top10/", views.deals_top10, name="deals_top10"),
    path("deals/create/", views.deal_create, name="deal_create"),

    path("module2/", qr_views.qr_form_view, name="module2"),
    path("qr/", include(("internship_b24.qr.urls", "qr"), namespace="qr")),
    path("product/", include(("internship_b24.qr.public_urls", "qr_public"), namespace="qr_public")),

    path("module3/", views.module3, name="module3"),
    path("module4/", views.module4, name="module4"),
    path("module5/", views.module5, name="module5"),
    path("oauth/bitrix/", views.oauth_bitrix, name="oauth_bitrix"),


]
