from django import forms
from .models import *


class CategoryForm(forms.ModelForm):

        
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(shop=shop)
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        
    class Meta:
        model = Product
        fields = ['name', 'cost_price', 'sale_price', 'bar_code', 'quantity', 'min_quantity', 'unit', 'discount', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bar_code': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean_discount(self):
        discount = self.cleaned_data.get('discount', 0)
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Скидка должна быть в диапазоне от 0 до 100.")
        return discount