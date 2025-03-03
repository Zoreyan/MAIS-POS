from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from .models import *
from apps.finance.models import Expense
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .filters import OrderHistoryFilter, SoldHistoryFilter, IncomeHistoryFilter
from apps.product.utils import paginate

@login_required

def total(request):
    orders = OrderHistory.objects.filter(shop=request.user.shop).order_by('-created')
    filters = OrderHistoryFilter(request.GET, queryset=orders)

    page_number = request.GET.get('page')
    
    page_obj, visible_pages = paginate(request, filters.qs, page_number)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters
    }

    return render(request, 'history/total.html', context)


@login_required
def sales(request):
    sales = SoldHistory.objects.filter(shop=request.user.shop).order_by('-created')

    filters = SoldHistoryFilter(request.GET, queryset=sales)
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters
    }
    return render(request, 'history/sales.html', context)


@login_required
def incomes(request):
    incomes = IncomeHistory.objects.filter(shop=request.user.shop).order_by('-created')
    filters = IncomeHistoryFilter(request.GET, queryset=incomes)
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters
    }
    return render(request, 'history/incomes.html', context)


@login_required
def sales_delete(request, pk):
    sale = SoldHistory.objects.get(id=pk)
    sale.product.quantity += sale.quantity
    sale.product.save()
    sale.delete()
    return redirect('sold-history')


@login_required
def income_delete(request, pk):
    income = IncomeHistory.objects.get(id=pk)
    product = income.product
    product.quantity -= income.quantity
    product.save()
    income.delete()
    return redirect('income-history')


@login_required
def order_delete(request, pk):
    # Получаем заказ по ID
    order = OrderHistory.objects.get(id=pk)

    if order.order_type == 'sale':
        for i in order.soldhistory_set.all():
            product = i.product
            product.quantity += i.quantity
            product.save()
    else:
        for i in order.incomehistory_set.all():
            product = i.product
            product.quantity -= i.quantity
            product.save()

        Expense.objects.filter(
            shop=order.shop,
            expend_type='supplies',
            amount=order.amount,
        ).delete()

    order.delete()

    return redirect('total')
