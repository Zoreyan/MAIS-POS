from django import forms

from .models import *


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        if shop:
            self.fields['parent'].queryset = Category.objects.filter(shop=shop)
        self.fields['parent'].widget.attrs.update({'class': 'form-select'})
        
    class Meta:
        model = Category
        fields = ['name', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'sale_price', 'image', 'bar_code', 'quantity', 'unit', 'discount', 'description', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bar_code': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean_discount(self):
        discount = self.cleaned_data.get('discount', 0)
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Скидка должна быть в диапазоне от 0 до 100.")
        return discount

