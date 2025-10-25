from django import forms

class QRForm(forms.Form):
    search = forms.CharField(
        required=False,
        label="Поиск товара",
        widget=forms.TextInput(attrs={
            "placeholder": "Начните вводить название товара…",
            "autocomplete": "off",
        })
    )
    product_id = forms.IntegerField(
        required=True,
        label="ID товара *",
        widget=forms.NumberInput(attrs={"placeholder": "ID товара"})
    )
