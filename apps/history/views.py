from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from .models import *
from django.contrib.auth.decorators import login_required

@login_required
def history(request):
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

    context = {
        'orders': orders,
        'date_from': date_from,
        'date_to': date_to,
        'order_type': order_type,
    }

    return render(request, 'history/history.html', context)



def sales(request):
    sales = SoldHistory.objects.filter(shop=request.user.shop).order_by('-created')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        sales = sales.filter(created__gte=date_from)

    if date_to:
        sales = sales.filter(created__lte=date_to)
        
    context = {
        'sales': sales
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

    context = {
        'incomes': incomes,
        'date_from': date_from,
        'date_to': date_to
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
    return redirect('history')