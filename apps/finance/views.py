from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.db.models import Sum
from .models import Expense
from apps.history.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_POST
import json



def list(request):
    expenses = Expense.objects.filter(shop=request.user.shop).order_by('-created')
    context = {
        'expenses': expenses
    }
    
    return render(request, 'finance/list.html', {'expenses': expenses})


def create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.shop = request.user.shop
            expense.save()
            return redirect('finance-list')
    else:
        form = ExpenseForm()
    return render(request, 'finance/create.html', {'form': form})