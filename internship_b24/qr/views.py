import base64
from io import BytesIO

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_GET

import qrcode

from .forms import QRForm
from .models import ProductLink
from .services import get_product_by_id, search_products_by_name


def _build_public_url(request, token) -> str:
    return request.build_absolute_uri(
        reverse("internship_b24:qr_public:product_public", args=[str(token)])
    )

def _make_qr_data_uri(link_url: str) -> str:
    img = qrcode.make(link_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


@require_http_methods(["GET", "POST"])
def qr_form_view(request):
    form = QRForm(request.POST or None)
    ctx = {"form": form}

    if request.method == "POST" and form.is_valid():
        product_id = form.cleaned_data["product_id"]

        product = get_product_by_id(product_id)
        if not product:
            form.add_error("product_id", "Товар не найден в Битрикс24")
        else:
            pl = ProductLink.objects.create(
                product_id=product.id,
                title_cached=product.name,
                img_url_cached=product.image or "",
                price_cached=product.price or "",
                currency_cached=product.currency or "",
                description_cached=product.description or "",
                created_by=str(request.user) if request.user.is_authenticated else "",
            )
            return redirect("internship_b24:qr:qr_success", token=str(pl.id))

    return render(request, "qr/qr_form.html", ctx)



def qr_success_view(request, token: str):
    pl = get_object_or_404(ProductLink, pk=token)
    public_url = _build_public_url(request, pl.pk)
    qr_data_uri = _make_qr_data_uri(public_url)

    ctx = {
        "pl": pl,
        "public_url": public_url,
        "qr_data_uri": qr_data_uri,

        "title": pl.title_cached,
        "picture": pl.img_url_cached,
        "price": pl.price_cached,
        "currency": pl.currency_cached,
        "product_id": pl.product_id,
    }
    return render(request, "qr/qr_success.html", ctx)



def product_public_view(request, token: str):
    pl = get_object_or_404(ProductLink, pk=token)

    live = get_product_by_id(pl.product_id)

    if live:
        title = live.name or pl.title_cached
        picture = live.image or pl.img_url_cached
        price_text = live.price
        currency = live.currency
        description = live.description or pl.description_cached
    else:
        title = pl.title_cached or f"Товар {pl.product_id}"
        picture = pl.img_url_cached
        price_text = pl.price_cached
        currency = pl.currency_cached
        description = pl.description_cached

    ctx = {
        "title": title,
        "picture": picture,
        "price": price_text,
        "currency": currency,
        "description": description,
        "product_id": pl.product_id,
        "link_id": pl.pk,
    }
    return render(request, "qr/product_public.html", ctx)



@require_GET
def api_product_search(request):
    q = request.GET.get("q", "")
    products = search_products_by_name(q)

    data = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "currency": p.currency,
        }
        for p in products
    ]

    return JsonResponse({"results": data})
