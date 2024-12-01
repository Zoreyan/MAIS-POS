from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ['type', 'description', 'created', 'amount', 'image']
        widgets = {
            'created': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'По дату'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Сумма'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
