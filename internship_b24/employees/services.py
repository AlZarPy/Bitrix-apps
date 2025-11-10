from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


def b24_call(request, method: str, params=None):
    """
    Унифицированный вызов Bitrix24.

    - crm.* / user.get / department.get / voximplant.statistic.get:
      через call_list_method(fields=...)
    - telephony.externalCall.register / telephony.externalCall.finish:
      через call_api_method(params)
    - остальные методы: по умолчанию через call_api_method(params)
    """
    params = params or {}
    but = request.bitrix_user_token

    if method.startswith("crm.") or method in (
        "user.get",
        "department.get",
        "voximplant.statistic.get",
    ):
        return but.call_list_method(method, fields=params)

    return but.call_api_method(api_method=method, params=params)


def fetch_active_users(request) -> List[Dict[str, Any]]:
    """Возвращает список активных пользователей."""
    users = b24_call(request, "user.get", {"ACTIVE": "Y"})
    return users if isinstance(users, list) else []


def fetch_departments(request) -> Dict[int, Dict[str, Any]]:
    """Карта департаментов: dept_id -> {ID, NAME, UF_HEAD, PARENT}."""
    dept_list = b24_call(request, "department.get", {})
    depts: Dict[int, Dict[str, Any]] = {}

    for d in dept_list or []:
        try:
            did = int(d["ID"])
        except Exception:
            continue
        depts[did] = {
            "ID": did,
            "NAME": d.get("NAME"),
            "UF_HEAD": int(d["UF_HEAD"]) if d.get("UF_HEAD") else None,
            "PARENT": int(d["PARENT"]) if d.get("PARENT") else None,
        }

    return depts


def build_manager_chain(
    user: Dict[str, Any],
    depts: Dict[int, Dict[str, Any]],
    users_by_id: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Цепочка руководителей «от ближайшего к верхнему» по PARENT департаментов.
    На каждом уровне берём UF_HEAD (если есть и это не сам пользователь).
    """
    chain_ids: List[int] = []
    dept_ids = user.get("UF_DEPARTMENT") or []
    cur: Optional[int] = int(dept_ids[0]) if dept_ids else None
    visited: set[int] = set()

    while cur and cur not in visited:
        visited.add(cur)
        dept = depts.get(cur)
        if not dept:
            break
        head_id = dept.get("UF_HEAD")
        if head_id and head_id != int(user["ID"]):
            chain_ids.append(head_id)
        cur = dept.get("PARENT")

    chain: List[Dict[str, Any]] = []
    for mid in chain_ids:
        u = users_by_id.get(mid)
        if not u:
            continue
        name = f'{u.get("NAME", "")} {u.get("LAST_NAME", "")}'.strip()
        chain.append({"id": mid, "name": name})

    return chain


def count_outbound_calls_24h(request, user_id: int) -> int:
    """
    Количество звонков за последние 24 часа
    по заданным критериям (см. FILTER ниже).
    """
    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(hours=24)

    res = b24_call(request, "voximplant.statistic.get", {
        "FILTER": {
            "PORTAL_USER_ID": int(user_id),
            "CALL_TYPE": "1",
            ">CALL_DURATION": 60,
            ">CALL_START_DATE": from_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
    })

    items = res if isinstance(res, list) else (res.get("result", []) if isinstance(res, dict) else [])
    return len(items)


def generate_test_calls(request, user_ids: List[int], per_user: int = 3) -> None:
    """
    Генерирует per_user тестовых звонков для каждого пользователя.
    Параметры и пауза подобраны под текущую рабочую конфигурацию.
    """
    from random import randint

    now = datetime.now(timezone.utc)

    # дефолтная линия (если нужна порталу)
    try:
        cfg = b24_call(request, "telephony.config.get", {})
    except Exception:
        cfg = {}
    default_line = (cfg or {}).get("DEFAULT_LINE")

    for uid in user_ids:
        for _ in range(max(0, per_user)):
            start_dt = now - timedelta(minutes=randint(0, 23 * 60))
            duration = randint(1, 180)
            phone = f"+7999{randint(1_000_000, 9_999_999)}"

            reg_payload = {
                "USER_ID": int(uid),
                "PHONE_NUMBER": phone,
                "TYPE": 1,
                "SHOW": 0,
                "CALL_START_DATE": start_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            if default_line:
                reg_payload["LINE_NUMBER"] = default_line

            reg = b24_call(request, "telephony.externalCall.register", reg_payload)

            if isinstance(reg, dict):
                call_id = (
                    reg.get("CALL_ID")
                    or (isinstance(reg.get("result"), dict) and reg["result"].get("CALL_ID"))
                    or reg.get("ID")
                )
            else:
                call_id = reg

            if not call_id:
                continue

            b24_call(request, "telephony.externalCall.finish", {
                "CALL_ID": call_id,
                "USER_ID": int(uid),
                "DURATION": duration,
                "STATUS_CODE": 200,
                "FAILED_REASON": "",
                "RECORD_URL": "",
            })

            time.sleep(0.5)
