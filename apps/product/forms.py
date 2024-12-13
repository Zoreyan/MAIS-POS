<<<<<<< HEAD
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
        fields = ['name', 'address', 'image', 'opening_hours', 'contacts', 'about', 'coordinates']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'opening_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'contacts': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control'}),
            'coordinates': forms.TextInput(attrs={'class': 'form-control'}),
        }

=======
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

>>>>>>> 0f5feb102b45a94eef3b618ce0c3188881e35ea1
