from html import unescape

UF_PRIORITY_CODE = 'UF_CRM_1760383363428'

def load_manuals(but):
    deal_fields = but.call_list_method('crm.deal.fields')
    stages      = but.call_list_method('crm.status.entity.items', fields={'entityId': 'DEAL_STAGE'})
    deal_types  = but.call_list_method('crm.status.entity.items', fields={'entityId': 'DEAL_TYPE'})
    currencies  = but.call_list_method('crm.currency.list')

    manuals = {
        'STAGE_ID':    {e['STATUS_ID']: e['NAME'] for e in stages},
        'TYPE_ID':     {e['STATUS_ID']: e['NAME'] for e in deal_types},
        'CURRENCY_ID': {e['CURRENCY']:  unescape(e['FULL_NAME']) for e in currencies},
    }

    for code, meta in deal_fields.items():
        if code.startswith('UF_CRM_') and isinstance(meta, dict) and meta.get('items'):
            manuals[code] = {i['ID']: i['VALUE'] for i in meta['items']}
            manuals[f'{code}__label'] = meta.get('formLabel') or meta.get('title') or code

    return deal_fields, manuals


def humanize_deal_row(row: dict, manuals: dict) -> dict:
    """Подменяет машинные коды читаемыми подписями в одной строке сделки."""
    row['TYPE_ID_H']   = manuals['TYPE_ID'].get(row.get('TYPE_ID'), row.get('TYPE_ID'))
    row['STAGE_ID_H']  = manuals['STAGE_ID'].get(row.get('STAGE_ID'), row.get('STAGE_ID'))
    row['CURRENCY_H']  = manuals['CURRENCY_ID'].get(row.get('CURRENCY_ID'), row.get('CURRENCY_ID'))
    row['UF_PRIORITY_H'] = manuals.get(UF_PRIORITY_CODE, {}).get(row.get(UF_PRIORITY_CODE)) \
                           if UF_PRIORITY_CODE in row else None
    return row
