from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from .models import *
from apps.finance.models import Expense
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

@login_required
def total(request):
    orders = OrderHistory.objects.filter(shop=request.user.shop).order_by('-created')

    # Получаем параметры фильтра
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    order_type = request.GET.get('order_type')

    # Применяем фильтрацию по дате (если указана)
    if date_from:
        orders = orders.filter(created__gte=date_from)
    if date_to:
        orders = orders.filter(created__lte=date_to)

    # Фильтрация по типу продажи или поступления
    if order_type:
        orders = orders.filter(order_type=order_type)

    # Для каждого заказа находим первый товар из списка SoldHistory или IncomeHistory
    for order in orders:
        # Изначально установим first_product в None
        first_product = None

        # Если это заказ на продажу (SoldHistory)
        if order_type == 'sale':
            first_product = order.soldhistory_set.first()
        # Если это заказ на поступление (IncomeHistory)
        elif order_type == 'entrance':
            first_product = order.incomehistory_set.first()

        # Сохраняем первый товар для отображения
        order.first_product = first_product.product if first_product else None

    orders_per_page = request.user.shop.orderhistory_per_page
    paginator = Paginator(orders, orders_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ограничение отображаемых страниц
    current_page = page_obj.number
    total_pages = paginator.num_pages
    delta = 5  # Количество страниц до и после текущей

    start_page = max(current_page - delta, 1)
    end_page = min(current_page + delta, total_pages)
    visible_pages = range(start_page, end_page + 1)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'date_from': date_from,
        'date_to': date_to,
        'order_type': order_type,
        'number_per_page':orders_per_page
    }

    return render(request, 'history/total.html', context)

def sales(request):
    sales = SoldHistory.objects.filter(shop=request.user.shop).order_by('-created')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        sales = sales.filter(created__gte=date_from)

    if date_to:
        sales = sales.filter(created__lte=date_to)

    sales_per_page = request.user.shop.salehistory_per_page
    paginator = Paginator(sales, sales_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ограничение отображаемых страниц
    current_page = page_obj.number
    total_pages = paginator.num_pages
    delta = 5  # Количество страниц до и после текущей

    start_page = max(current_page - delta, 1)
    end_page = min(current_page + delta, total_pages)
    visible_pages = range(start_page, end_page + 1)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'date_from': date_from,
        'date_to': date_to,
        'number_per_page':sales_per_page
    }
    return render(request, 'history/sales.html', context)

def incomes(request):
    incomes = IncomeHistory.objects.filter(shop=request.user.shop).order_by('-created')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        incomes = incomes.filter(created__gte=date_from)

    if date_to:
        incomes = incomes.filter(created__lte=date_to)

    incomes_per_page = request.user.shop.incomehistory_per_page
    paginator = Paginator(incomes, incomes_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Ограничение отображаемых страниц
    current_page = page_obj.number
    total_pages = paginator.num_pages
    delta = 5  # Количество страниц до и после текущей

    start_page = max(current_page - delta, 1)
    end_page = min(current_page + delta, total_pages)
    visible_pages = range(start_page, end_page + 1)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'date_from': date_from,
        'date_to': date_to,
        'number_per_page':incomes_per_page
    }
    return render(request, 'history/incomes.html', context)


def sales_delete(request, pk):
    sale = SoldHistory.objects.get(id=pk)
    sale.product.quantity += sale.quantity
    sale.product.save()
    sale.delete()
    return redirect('sold-history')


def income_delete(request, pk):
    income = IncomeHistory.objects.get(id=pk)
    product = income.product
    product.quantity -= income.quantity
    product.save()
    income.delete()
    return redirect('income-history')

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
