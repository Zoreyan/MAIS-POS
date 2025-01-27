from django import forms
from apps.product.models import Shop
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from django.utils.datastructures import MultiValueDict


class CreateUserForm(UserCreationForm):

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username', 'get_email_notification', 'email', 'password1', 'password2', 'role', 'first_name', 'last_name', 'image', 'phone']

        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
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
            }),
            'get_email_notification' : forms.CheckboxInput(
                    attrs={
                    'class': 'form-check-input',  # Класс для переключателя
                    'role': 'switch',  # Атрибут для дополнительной стилизации (если требуется)
                    'id': 'flexSwitchCheckDefault',  # ID для связки с <label>
                    }
                ),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'get_email_notification', 'first_name', 'last_name', 'image', 'phone', 'email', 'role']
        
        
        widgets = {
           'email': forms.EmailInput(attrs={
                'class':'form-control',
                'id':'email'
            }),
            'role': forms.Select(attrs={
                'class':'form-select',
                'id':'role'
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
                'class': 'form-control',
            }),
            'get_email_notification' : forms.CheckboxInput(
                    attrs={
                    'class': 'form-check-input',  # Класс для переключателя
                    'role': 'switch',  # Атрибут для дополнительной стилизации (если требуется)
                    'id': 'flexSwitchCheckDefault',  # ID для связки с <label>
                    }
                ),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'get_email_notification', 'first_name', 'last_name', 'image', 'phone', 'email']
        
        
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
                'class': 'form-control',
            }),
            'get_email_notification' : forms.CheckboxInput(
                    attrs={
                    'class': 'form-check-input',  # Класс для переключателя
                    'role': 'switch',  # Атрибут для дополнительной стилизации (если требуется)
                    'id': 'flexSwitchCheckDefault',  # ID для связки с <label>
                    }
                ),
        }

class UserForm(UserCreationForm):
    # Вы можете добавить дополнительные поля здесь, если они необходимы для пользователя
    email = forms.EmailField(required=True)

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'username')

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'address', 'coordinates', 'contacts', 'about', 'opening_hours',]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class':'form-control',
                'id':'name',
                'placeholder':'Название магазина'
            }),
            'address': forms.TextInput(attrs={
                'class':'form-control',
                'id':'address',
                'placeholder':'Адрес магазина'
            }),
            'coordinates': forms.TextInput(attrs={
                'class':'form-control',
                'id':'coordinates',
                'placeholder':'Координаты магазина'
            }),
            'contacts': forms.TextInput(attrs={
                'class':'form-control',
                'id':'contacts',
                'placeholder':'Контакты магазина'
            }),
            'about': forms.Textarea(attrs={
                'class':'form-control',
                'id':'about',
                'placeholder':'Описание магазина',
                'rows':3
            }),
            'opening_hours': forms.Textarea(attrs={
                'class':'form-control',
                'id':'opening_hours',
                'placeholder':'Часы работы магазина',
                'rows':3
            }),
        }