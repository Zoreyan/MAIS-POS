from django import forms
from .models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'sale_price', 'image', 'bar_code', 'quantity', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bar_code': forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
        }


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'address', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }