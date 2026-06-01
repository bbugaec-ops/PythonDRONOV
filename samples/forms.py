from django import forms
from .models import Bd, Order

class BdForm(forms.ModelForm):
    class Meta:
        model = Bd
        fields = ('title', 'content', 'price', 'rubric', 'image')

class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо клас Bootstrap всім полям
        for field in self.fields:
            if field == 'delivery_service':
                self.fields[field].widget.attrs.update({'class': 'form-select'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Order
        # ВАЖЛИВО: 'street' тепер у списку, тому він отримає рамку
        fields = [
            'last_name',
            'first_name',
            'middle_name',
            'email',
            'phone',
            'region',
            'delivery_type',
            'city',
            'street',  # Поле додано сюди
            'delivery_service',
            'department'
        ]