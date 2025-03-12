from .filters import OrderHistoryFilter, SoldHistoryFilter, IncomeHistoryFilter, LogHistoryFilter
from django.db.models import Q, Sum, F
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.utils.utils import paginate
from django.utils.timezone import now
from datetime import timedelta
from .models import *

@login_required

def total(request):
    shop = request.user.shop
    orders = OrderHistory.objects.filter(shop=shop).order_by('-created')
    filters = OrderHistoryFilter(request.GET, queryset=orders)

    # Получение даты начала и конца текущего месяца
    today = now().date()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Получение значений из запроса или установка значений по умолчанию
    date_gte = request.GET.get('created_min', first_day)
    date_lte = request.GET.get('created_max', last_day)

    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number)

    # Общий доход от продаж
    total_sales = SoldHistory.objects.filter(Q(created__gte=date_gte), Q(created__lte=date_lte), Q(shop=shop))\
        .annotate(total_per_sale=F('amount') * F('quantity'))\
        .aggregate(total_sales=Sum('total_per_sale'))['total_sales'] or 0

    # Общее количество проданных товаров
    total_sales_quantity = SoldHistory.objects.filter(Q(shop=shop) & Q(created__gte=date_gte) & Q(created__lte=date_lte))\
        .aggregate(total_sum=Sum('quantity'))['total_sum'] or 0

    # Средний чек
    try:
        average_receipt = round(total_sales / total_sales_quantity)
    except ZeroDivisionError:
        average_receipt = 0

    # Самый продаваемый товар
    top_product = SoldHistory.objects.filter(Q(created__gte=date_gte), Q(created__lte=date_lte), Q(shop=shop))\
        .values('product__name', 'product__id')\
        .annotate(total_quantity=Sum('quantity'))\
        .order_by('-total_quantity')\
        .first()

    top_selling_product = {
        "name": top_product['product__name'] if top_product else "Нет данных",
        "quantity": top_product['total_quantity'] if top_product else 0,
    }

    # Оплаты наличными
    cash_total = OrderHistory.objects.filter(shop=shop, created__gte=date_gte, created__lte=date_lte)\
        .aggregate(total_cash=Sum('cash_payment'))['total_cash'] or 0

    # Оплаты картой
    card_total = OrderHistory.objects.filter(shop=shop, created__gte=date_gte, created__lte=date_lte)\
        .aggregate(total_card=Sum('online_payment'))['total_card'] or 0

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'average_receipt': average_receipt,
        'top_selling_product': top_selling_product,
        'cash_payments': cash_total,
        'card_transfers': card_total,
        'filters': filters,
        'date_gte': date_gte,
        'date_lte': date_lte
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
    LogHistory.objects.create(user=request.user, message='Удалена продажа', shop=request.user.shop, object=sale.product.name)
    sale.delete()

    return redirect('sold-history')


@login_required
def income_delete(request, pk):
    income = IncomeHistory.objects.get(id=pk)
    product = income.product
    product.quantity -= income.quantity
    product.save()
    LogHistory.objects.create(user=request.user, message='Удалена поставка', shop=request.user.shop, object=product.name)
    income.delete()
    return redirect('income-history')


@login_required
def order_delete(request, pk):
    # Получаем заказ по ID
    order = OrderHistory.objects.get(id=pk)

    for i in order.soldhistory_set.all():
        product = i.product
        product.quantity += i.quantity
        product.save()
    
    LogHistory.objects.create(user=request.user, message='Удалена очередь', shop=request.user.shop, object=f'{order.id} - {order.created}')
    order.delete()

    return redirect('total')


def log_list(request):
    logs = LogHistory.objects.filter(shop=request.user.shop).order_by('-created')
    filters = LogHistoryFilter(request.GET, queryset=logs)
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number)
    context = {
        'logs': logs,
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters
    }
    return render(request, 'history/logs.html', context)

