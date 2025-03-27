from apps.utils.utils import check_permission, delete_obj, paginate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .filters import ExpenseFilter
from .models import Expense
from .models import *
from .forms import *
from apps.history.models import LogHistory

@login_required
@check_permission
def finance_list(request):

    expenses = Expense.objects.filter(shop=request.user.shop).order_by('-created')
    filters = ExpenseFilter(request.GET, queryset=expenses)
    number_per_page = request.user.shop.finance_per_page
    
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number, number_per_page)
    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters,
        'number_per_page':number_per_page
    }
    
    return render(request, 'finance/list.html', context)

@login_required
@check_permission
def create(request):
    

    expend_type = request.GET.get('type')
    if not expend_type:
        return redirect('finance-list')

    expend_display_name = dict(Expense.EXPENSE_TYPES).get(expend_type)
    form = ExpenseForm(initial={'expend_type': expend_type}, shop=request.user.shop) 
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, shop=request.user.shop)
        if form.is_valid():
            expend = form.save(commit=False)
            expend.shop = request.user.shop
            expend.expend_type = expend_type
            expend.shop = request.user.shop
            if expend_type == 'other':
                expend.description = form.cleaned_data['description']
            else:
                expend.description = expend_display_name
            LogHistory.objects.create(user=request.user, message='Добавлен расход', object=expend_type)
            expend.save()
            
            return redirect('finance-list')  # Перенаправление на список расходов
    
    context = {
        'form': form,
        'expend_type': expend_type,
        'expend_display_name': expend_display_name
    }
    return render(request, 'finance/create.html', context)

@login_required
@check_permission
def expense_delete(request, pk):
    delete_obj(request, Expense, pk, 'Удален расход')
    return redirect('finance-list')