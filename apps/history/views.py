from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from .models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

def update_orders_per_page(request):
    if request.method == "POST":
        try:
            orders_per_page = int(request.POST.get("orders_per_page", 10))
            if orders_per_page > 0:
                request.session['orders_per_page'] = orders_per_page
        except ValueError:
            request.session['orders_per_page'] = 10
    return redirect('settings')

@login_required
def total(request):
    orders = OrderHistory.objects.filter(shop=request.user.shop).order_by('-created')

    orders_per_page = request.session.get('orders_per_page', 10)
    paginator = Paginator(orders, orders_per_page)
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
        'page_obj': page_obj,
        'visible_pages': visible_pages,
    }

    return render(request, 'history/total.html', context)

def update_sales_per_page(request):
    if request.method == "POST":
        try:
            sales_per_page = int(request.POST.get("sales_per_page", 10))
            if sales_per_page > 0:
                request.session['sales_per_page'] = sales_per_page
        except ValueError:
            request.session['sales_per_page'] = 10
    return redirect('settings')

def sales(request):
    sales = SoldHistory.objects.filter(shop=request.user.shop).order_by('-created')

    sales_per_page = request.session.get('sales_per_page', 10)
    paginator = Paginator(sales, sales_per_page)
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
        'page_obj': page_obj,
        'visible_pages': visible_pages,
    }
    return render(request, 'history/sales.html', context)

def update_incomes_per_page(request):
    if request.method == "POST":
        try:
            incomes_per_page = int(request.POST.get("incomes_per_page", 10))
            if incomes_per_page > 0:
                request.session['incomes_per_page'] = incomes_per_page
        except ValueError:
            request.session['incomes_per_page'] = 10
    return redirect('settings')

def incomes(request):
    incomes = IncomeHistory.objects.filter(shop=request.user.shop).order_by('-created')

    incomes_per_page = request.session.get('incomes_per_page', 10)
    paginator = Paginator(incomes, incomes_per_page)
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
        'page_obj': page_obj,
        'visible_pages': visible_pages,
    }
    return render(request, 'history/incomes.html', context)


def sales_delete(request, pk):
    sale = SoldHistory.objects.get(id=pk)
    sale.product.quantity += sale.quantity
    sale.product.save()
    sale.delete()
    return redirect('sold-history')


def incomes_delete(request, pk):
    income = IncomeHistory.objects.get(id=pk)
    product = income.product
    product.quantity -= income.quantity
    product.save()
    income.delete()
    return redirect('income-history')

def order_delete(request, pk):
    order = OrderHistory.objects.get(id=pk)
    for i in order.soldhistory_set.all():
        product = i.product
        product.quantity += i.quantity
        product.save()
    order.delete()
    return redirect('total')

def income_delete(request, pk):
    income = Income.objects.get(id=pk)
    for i in income.incomehistory_set.all():
        product = i.product
        product.quantity -= i.quantity
        product.save()
    income.delete()
    return redirect('total')