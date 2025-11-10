import json

from django.conf import settings
from django.shortcuts import render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth


def b24_call(request, method: str, params=None):
    """
    Унифицированный вызов Bitrix24.

    crm.* и crm.address.* → call_list_method(fields=...)
    остальное → call_api_method(params)
    """
    params = params or {}
    but = request.bitrix_user_token

    if method.startswith("crm."):
        return but.call_list_method(method, fields=params)

    return but.call_api_method(api_method=method, params=params)


@main_auth(on_cookies=True)
def companies_map_view(request):
    """
    Страница с картой компаний.

    1) Берём активные компании (ID, TITLE).
    2) Берём адреса из crm.address.list.
    3) Склеиваем по ENTITY_ID → получаем список компаний с адресами.
    4) Отдаём на фронт, там уже geocode через Yandex JS API.
    """

    # 1. Компании
    companies_resp = b24_call(request, "crm.company.list", {
        "filter": {"ACTIVE": "Y"},
        "select": ["ID", "TITLE"],
        "order": {"ID": "ASC"},
    })

    if isinstance(companies_resp, dict):
        companies_raw = companies_resp.get("result", [])
    else:
        companies_raw = companies_resp or []

    # 2. Адреса
    addresses_resp = b24_call(request, "crm.address.list", {
        "select": [
            "ENTITY_ID",
            "ADDRESS_1",
            "CITY",
            "REGION",
            "COUNTRY",
        ],
        # Можно отфильтровать только компании:
        # "filter": {"ENTITY_TYPE_ID": 4},
    })

    if isinstance(addresses_resp, dict):
        addresses_raw = addresses_resp.get("result", [])
    else:
        addresses_raw = addresses_resp or []

    # 3. Собираем словарь: company_id -> строка адреса
    address_by_company_id = {}

    for a in addresses_raw:
        if not isinstance(a, dict):
            continue

        # ID сущности (компании)
        cid = str(a.get("ENTITY_ID") or "").strip()
        if not cid:
            continue

        parts = [
            a.get("COUNTRY"),
            a.get("REGION"),
            a.get("CITY"),
            a.get("ADDRESS_1"),
        ]
        addr = ", ".join(p for p in parts if p)

        if addr:
            address_by_company_id[cid] = addr

    # 4. Формируем итоговый список компаний с адресом
    companies = []
    for c in companies_raw:
        if not isinstance(c, dict):
            continue

        cid = str(c.get("ID") or "").strip()
        if not cid:
            continue

        addr = address_by_company_id.get(cid)
        if not addr:
            # Без адреса на карте не показываем
            continue

        title = (c.get("TITLE") or "").strip() or f"Компания #{cid}"
        companies.append({
            "id": cid,
            "title": title,
            "address": addr,
        })

    context = {
        "companies_json": json.dumps(companies, ensure_ascii=False),
        "yandex_api_key": getattr(settings, "YANDEX_API_KEY", ""),
        "has_companies": bool(companies),
    }
    return render(request, "map/map.html", context)
