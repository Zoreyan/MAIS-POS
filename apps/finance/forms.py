from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = shop.user_set.all()
    expend_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = Expense
        fields = ['expend_type', 'description', 'amount', 'user', 'image']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Сумма'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
