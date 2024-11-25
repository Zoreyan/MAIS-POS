from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm



class CreateUserForm(UserCreationForm):

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'first_name', 'last_name', 'image', 'phone']

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'role', 'first_name', 'last_name', 'image']
        
        
        widgets = {
            'role': forms.Select(attrs={
                'class':'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class':'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class':'form-control'
            }),
            'username': forms.TextInput(attrs={
                'class':'form-control'
            })
        }

