from django import forms
from .models import *


class CreateUserForm(forms.Form):
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
        ('cashier', 'Кассир'),
        ('owner', 'Владелец'),

    ]
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class':'form-control',
                'id':'email'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'id':'first_name'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'id':'last_name'
    }))
    phone = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class':'form-control',
        'id':'phone'
    }))
    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'form-control',
    }))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select',
    }))
   

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'image', 'phone', 'email']
        
        
        widgets = {
           'email': forms.EmailInput(attrs={
                'class':'form-control',
                'id':'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class':'form-control',
                'id':'first_name'
            }),
            'last_name': forms.TextInput(attrs={
                'class':'form-control',
                'id':'last_name'
            }),
            'phone': forms.TextInput(attrs={
                'class':'form-control',
                'id':'phone'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'upload',
                'style': 'display: none;'
            }),

        }

