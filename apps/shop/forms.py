from django import forms
from apps.product.models import Shop

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'address', 'image', 'opening_hours', 'contacts', 'about', 'coordinates']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'image', 'style': 'display: none;'}),
            'opening_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'contacts': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control'}),
            'coordinates': forms.TextInput(attrs={'class': 'form-control'}),
        }
