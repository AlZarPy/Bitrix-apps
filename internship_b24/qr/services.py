from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Tuple
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ProductInfo:
    id: int
    name: str
    price: str
    currency: str
    description: str
    image: str


# функция вызова Bitrix24
def _bx24_call(method: str, params: dict) -> Optional[dict]:
    """
    Универсальный REST-вызов к Bitrix24 через входящий вебхук.
    Мы читаем URL из settings.BITRIX_WEBHOOK_BASE.
    """
    base = getattr(settings, "BITRIX_WEBHOOK_BASE", "").rstrip("/")
    if not base:
        logger.warning("BITRIX_WEBHOOK_BASE is not configured")
        return None

    url = f"{base}/{method}"
    try:
        resp = requests.post(url, json=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning("BX24 REST call failed: %s", e)
        return None


# вспомогательные функции работы с товарами

def _get_product_raw(product_id: int) -> Tuple[Optional[dict], Optional[str]]:
    """
    Возвращает (product_dict, image_url) или (None, None)
    product_dict = результат crm.product.get
    image_url    = detailUrl из catalog.productImage.list
    """
    # 1. crm.product.get
    data = _bx24_call("crm.product.get", {"ID": product_id})
    product = data.get("result", {}) if isinstance(data, dict) else {}
    if not product:
        return None, None

    # 2. catalog.productImage.list (получить detailUrl картинки)
    img_url = ""
    data_img = _bx24_call("catalog.productImage.list", {
        "productId": product_id,
        "select": [
            "id", "name", "productId", "type", "createTime",
            "downloadUrl", "detailUrl"
        ]
    })
    if isinstance(data_img, dict):
        images = data_img.get("result", {}).get("productImages", [])
        if images:
            # берём первую
            img_url = images[0].get("detailUrl", "") or images[0].get("downloadUrl", "") or ""

    return product, img_url


def get_product_by_id(product_id: int) -> Optional[ProductInfo]:
    """
    Высокоуровневый метод.
    Возвращает удобный объект ProductInfo или None.
    """
    product_raw, image_url = _get_product_raw(product_id)
    if not product_raw:
        return None

    name = product_raw.get("NAME") or f"Товар {product_id}"
    price_val = product_raw.get("PRICE")
    currency = product_raw.get("CURRENCY_ID") or ""
    description = product_raw.get("DESCRIPTION") or ""

    # если цена None
    if price_val is None or price_val == "":
        price = ""
    else:
        price = str(price_val)

    return ProductInfo(
        id=int(product_id),
        name=name,
        price=price,
        currency=currency,
        description=description,
        image=image_url or "",
    )


def search_products_by_name(query: str, limit: int = 10) -> List[ProductInfo]:
    """
    Для автокомплита. Берём crm.product.list по %NAME.
    Возвращаем список ProductInfo c урезанными полями.
    Картинку тут не тянем, только имя/цену.
    """
    q = (query or "").strip()

    data = _bx24_call("crm.product.list", {
        "filter": {"%NAME": q} if q else {},
        "select": ["ID", "NAME", "PRICE", "CURRENCY_ID"],
        "order": {"ID": "DESC"},
        "start": -1,
    })

    results = []
    if isinstance(data, dict) and "result" in data:
        for r in data["result"][:limit]:
            pid = int(r["ID"])
            name = r.get("NAME") or f"Товар {pid}"
            price_val = r.get("PRICE")
            currency = r.get("CURRENCY_ID") or ""

            if price_val is None or price_val == "":
                price = ""
            else:
                price = str(price_val)

            results.append(ProductInfo(
                id=pid,
                name=name,
                price=price,
                currency=currency,
                description="",
                image="",  # не тянем тут
            ))

    return results
