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
from django.core.paginator import Paginator



def finance_list(request):
    expenses = Expense.objects.filter(shop=request.user.shop).order_by('-created')
    expense_types = ['rent', 'utilities', 'salaries', 'supplies', 'other']

    # Фильтр по дате начала
    date_from = request.GET.get('date_from')
    if date_from:
        expenses = expenses.filter(created__date__gte=date_from)

    # Фильтр по дате окончания
    date_to = request.GET.get('date_to')
    if date_to:
        expenses = expenses.filter(created__date__lte=date_to)

    expend_type = request.GET.get('expend_type')
    if expend_type:
        expenses = expenses.filter(expend_type=expend_type)

    finance_per_page = request.session.get('finance_per_page', 10)
    paginator = Paginator(expenses, finance_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ограничение отображаемых страниц
    current_page = page_obj.number
    total_pages = paginator.num_pages
    delta = 3  # Количество страниц до и после текущей

    start_page = max(current_page - delta, 1)
    end_page = min(current_page + delta, total_pages)
    visible_pages = range(start_page, end_page + 1)

    context = {
        'expense_types': expense_types,
        'page_obj': page_obj,
        'visible_pages': visible_pages,
    }
    
    return render(request, 'finance/list.html', context)

def update_finance_per_page(request):
    if request.method == "POST":
        try:
            finance_per_page = int(request.POST.get("finance_per_page", 10))
            if finance_per_page > 0:
                request.session['finance_per_page'] = finance_per_page
        except ValueError:
            request.session['finance_per_page'] = 10
    return redirect('settings')

def create(request):
    expend_type = request.GET.get('type')
    expend_display_name = dict(Expense.CHOICES).get(expend_type)
    form = ExpenseForm(initial={'expend_type': expend_type}) 
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expend = form.save(commit=False)
            expend.shop = request.user.shop
            expend.expend_type = expend_type
            expend.shop = request.user.shop
            if expend_type == 'other':
                expend.description = form.cleaned_data['description']
            else:
                expend.description = expend_display_name
            expend.save()
            
            return redirect('finance-list')  # Перенаправление на список расходов
    
    context = {
        'form': form,
        'expend_type': expend_type,
        'expend_display_name': expend_display_name
    }
    return render(request, 'finance/create.html', context)

def expense_delete(request, pk):
    expend = get_object_or_404(Expense, id=pk)
    expend.delete()
    return redirect('finance-list')