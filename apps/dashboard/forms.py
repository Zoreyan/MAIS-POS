from apps.product.models import Shop
from django import forms


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),}