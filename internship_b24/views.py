from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt

from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .services import load_manuals, humanize_deal_row, UF_PRIORITY_CODE


class NewDealForm(forms.Form):
    title = forms.CharField(label='Название *', max_length=255)

    # селекты будут наполняться в __init__ из manuals:
    type_id = forms.ChoiceField(label='Тип', required=False)
    currency_id = forms.ChoiceField(label='Валюта', required=False)
    uf_priority = forms.ChoiceField(label='Приоритет', required=False)

    opportunity = forms.DecimalField(
        label='Сумма', decimal_places=2, max_digits=18, required=False
    )
    begindate = forms.DateField(
        label='Дата начала', required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    closedate = forms.DateField(
        label='Дата завершения', required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    contact_id = forms.IntegerField(label='ID контакта (необяз.)', required=False)

    def __init__(self, *args, manuals=None, **kwargs):
        super().__init__(*args, **kwargs)
        m = manuals or {}

        # helper: пустой вариант первым пунктом
        def with_placeholder(dct):
            return [('', '—')] + [(k, v) for k, v in dct.items()]

        self.fields['type_id'].choices = with_placeholder(m.get('TYPE_ID', {}))
        self.fields['currency_id'].choices = with_placeholder(m.get('CURRENCY_ID', {}))
        self.fields['uf_priority'].choices = with_placeholder(m.get(UF_PRIORITY_CODE, {}))



@main_auth(on_start=True, set_cookie=True)
@xframe_options_exempt  # главная открывается во фрейме Б24
def index(request):
    """Главная с карточками модулей и выпадающим меню."""
    return render(request, "index.html")


@main_auth(on_cookies=True)
def deals_top10(request):
    """
    Таблица «10 последних активных сделок».
    Авторизация — по токену из cookies, который нам положил main_auth на главной.
    """
    but = request.bitrix_user_token
    deal_fields, manuals = load_manuals(but)

    rows = but.call_list_method('crm.deal.list', fields={
        'select': [
            'ID', 'TITLE', 'OPPORTUNITY', 'CURRENCY_ID',
            'STAGE_ID', 'TYPE_ID', 'BEGINDATE', 'CLOSEDATE',
            'DATE_CREATE', UF_PRIORITY_CODE
        ],
        'filter': {'CLOSED': 'N'},
        'order': {'DATE_CREATE': 'DESC'},
    })[:10]

    rows = [humanize_deal_row(r, manuals) for r in rows]

    return render(request, "deals_top10.html", {
        'rows': rows,
        'uf_priority_label': manuals.get(f'{UF_PRIORITY_CODE}__label', 'Приоритет'),
    })


@main_auth(on_cookies=True)
def deal_create(request):
    """
    Страница с формой создания сделки (GET) и обработка создания (POST).
    """
    but = request.bitrix_user_token
    _, manuals = load_manuals(but)

    if request.method == 'POST':
        form = NewDealForm(request.POST, manuals=manuals)
        if form.is_valid():
            cd = form.cleaned_data
            fields = {
                'TITLE': cd['title'],
                'OPPORTUNITY': cd.get('opportunity'),
                'CURRENCY_ID': cd.get('currency_id'),
                'TYPE_ID': cd.get('type_id'),
                'BEGINDATE': cd.get('begindate'),
                'CLOSEDATE': cd.get('closedate'),
                UF_PRIORITY_CODE: cd.get('uf_priority'),
            }
            if cd.get('contact_id'):
                fields['CONTACT_ID'] = cd['contact_id']

            new_id = but.call_list_method('crm.deal.add', fields={'fields': fields})
            _ = but.call_list_method('crm.deal.get', fields={'id': new_id})

            return redirect('internship_b24:deals_top10')
    else:
        form = NewDealForm(manuals=manuals)

    return render(request, "deal_create.html", {'form': form})


# Заглушки для остальных модулей
def module3(request): return HttpResponse("Модуль 3: заглушка")
def module4(request): return HttpResponse("Модуль 4: заглушка")
def module5(request): return HttpResponse("Модуль 5: заглушка")


def oauth_bitrix(request):
    return HttpResponse("OAuth handler OK", status=200)
