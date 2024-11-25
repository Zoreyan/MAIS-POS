from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ['type', 'description', 'created', 'amount']
        widgets = {
            'created': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'По дату'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Сумма'}),
        }
