from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле.', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'id': 'email',
        'placeholder': 'Email'
        }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'id': 'password1',
        'placeholder': 'Пароль'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'id': 'password2',
        'placeholder': 'Подтвердите пароль'
    }))
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


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
                'class': 'form-select'
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
        fields = ['username', 'first_name', 'last_name', 'image', 'phone', 'email']
        
        
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
            'username': forms.TextInput(attrs={
                'class':'form-control',
                'id':'username'
            }),
            'phone': forms.TextInput(attrs={
                'class':'form-control',
                'id':'phone'
            }),
            'image': forms.FileInput(attrs={
                'class': 'd-none',
                'id': 'upload'
            })
        }