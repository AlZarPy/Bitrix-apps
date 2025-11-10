from django.shortcuts import render, redirect
from django.contrib import messages

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .services import (
    fetch_active_users,
    fetch_departments,
    build_manager_chain,
    count_outbound_calls_24h,
    generate_test_calls,
)


@main_auth(on_cookies=True)
def employees_list_view(request):
    users = fetch_active_users(request)
    depts = fetch_departments(request)
    users_by_id = {int(u["ID"]): u for u in users}

    rows = []
    for u in users:
        uid = int(u["ID"])

        # Отдел
        dept_ids = u.get("UF_DEPARTMENT") or []
        dept_name = ""
        if dept_ids:
            try:
                d = depts.get(int(dept_ids[0]))
            except (TypeError, ValueError):
                d = None
            if d:
                dept_name = d.get("NAME", "") or ""

        # Должность (в Bitrix обычно поле POSITION)
        position = (u.get("WORK_POSITION") or u.get("POSITION") or "").strip()

        manager_chain = build_manager_chain(u, depts, users_by_id)
        calls = count_outbound_calls_24h(request, uid)

        rows.append({
            "id": uid,
            "name": f'{u.get("NAME", "")} {u.get("LAST_NAME", "")}'.strip(),
            "email": u.get("EMAIL"),
            "department": dept_name,
            "position": position,
            "managers": manager_chain,
            "calls_24h": calls,
        })

    rows.sort(
        key=lambda r: (
            (r["department"] or "ЯЯЯ").lower(),
            r["name"].lower()
        )
    )

    return render(request, "employees/list.html", {"rows": rows})



@main_auth(on_cookies=True)
def generate_calls_view(request):
    if request.method != "POST":
        return redirect("internship_b24:employees:list")

    try:
        per_user = int(request.POST.get("count", "10"))
    except (TypeError, ValueError):
        per_user = 10

    per_user = max(0, per_user)

    users = fetch_active_users(request)
    user_ids = [int(u["ID"]) for u in users]
    generate_test_calls(request, user_ids, per_user=per_user)

    messages.success(
        request,
        f"Сгенерированы тестовые звонки: по {per_user} шт. на пользователя."
    )
    return redirect("internship_b24:employees:list")
