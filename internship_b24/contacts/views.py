from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth

from .services import (
    parse_uploaded_file,
    import_contacts,
    export_contacts_to_csv,
    export_contacts_to_xlsx,
)


@main_auth(on_cookies=True)
def manage_view(request):
    return render(request, "contacts/manage.html")


@main_auth(on_cookies=True)
def import_view(request):
    if request.method == "POST":
        upload = request.FILES.get("file")
        if not upload:
            messages.error(request, "Файл не прикреплён.")
            return redirect("internship_b24:contacts:import")

        but = request.bitrix_user_token
        try:
            rows = parse_uploaded_file(upload)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("internship_b24:contacts:import")

        stats = import_contacts(but, rows)

        messages.success(
            request,
            (
                "Импорт завершён. "
                f"Создано: {stats['created']}, "
                f"дубли: {stats['skipped_duplicates']}, "
                f"пустые строки: {stats['skipped_empty']}."
            ),
        )
        return redirect("internship_b24:contacts:import")

    # GET — форма импорта
    return render(request, "contacts/import.html")


@main_auth(on_cookies=True)
def export_view(request):
    if request.method == "POST":
        fmt = (request.POST.get("format") or "csv").lower()
        date_from = (request.POST.get("date_from") or "").strip() or None
        date_to = (request.POST.get("date_to") or "").strip() or None
        company_filter = (request.POST.get("company") or "").strip() or None

        but = request.bitrix_user_token

        if fmt == "xlsx":
            data = export_contacts_to_xlsx(
                but=but,
                date_from=date_from,
                date_to=date_to,
                company_filter=company_filter,
            )
            response = HttpResponse(
                data,
                content_type=(
                    "application/"
                    "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )
            response["Content-Disposition"] = (
                'attachment; filename="contacts.xlsx"'
            )
            return response

        # по умолчанию — CSV
        data = export_contacts_to_csv(
            but=but,
            date_from=date_from,
            date_to=date_to,
            company_filter=company_filter,
        )
        response = HttpResponse(
            data,
            content_type="text/csv; charset=utf-8",
        )
        response["Content-Disposition"] = (
            'attachment; filename="contacts.csv"'
        )
        return response

    # GET — форма экспорта
    return render(request, "contacts/export.html")
