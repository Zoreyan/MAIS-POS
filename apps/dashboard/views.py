from django.shortcuts import render, redirect
from .models import *
from apps.history.models import *
from django.db.models import Sum, F, Avg
import json
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.product.models import Shop, Product
from apps.finance.models import Expense
from datetime import datetime
from apps.history.models import *
from datetime import datetime, timedelta
from django.db.models import Sum, F
from django.utils.timezone import make_aware, is_aware, now
import calendar
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
# import Map and Marker
from folium import Map, Marker
from django.utils.dateformat import DateFormat
from apps.user.utils import check_permission



@login_required
def get_sales_by_month(request):
    sales_by_month = SoldHistory.objects.annotate(
        month=TruncMonth('created')  # Группируем по месяцам
    ).values('month').annotate(
        total_sales=Sum('quantity')  # Суммируем продажи за каждый месяц
    ).order_by('month')

    return sales_by_month


@login_required
def get_chart_data(request):
    sales_by_month = get_sales_by_month(request)
    months = [sale['month'].strftime('%Y-%m') for sale in sales_by_month]  # Форматируем даты
    totals = [sale['total_sales'] for sale in sales_by_month]  # Суммы продаж

    return JsonResponse({'months': months, 'totals': totals})


def calculate_profit(request, shop, date):
    """
    Функция для вычисления прибыли.
    """

    sold_history = SoldHistory.objects.filter(shop=shop, created__date=date).aggregate(total_sum=Sum('quantity') * Sum('amount') - Sum('product__cost_price'))['total_sum'] or 0

    return sold_history

def calculate_revenue(request, shop, date):
    """
    Функция для вычисления прибыли.
    """

    sold_history = SoldHistory.objects.filter(shop=shop, created__date=date).aggregate(total_sum=Sum('quantity') * Sum('product__sale_price'))['total_sum'] or 0

    return sold_history


def calculate_sales(request, shop, date):
    """
    Функция для вычисления продаж.
    """
    sales = SoldHistory.objects.filter(shop=shop, created__date=date).aggregate(total_sum=Sum('quantity'))['total_sum'] or 0
    return sales


def calculate_growth(current, previous):
    """
    Функция для вычисления роста.
    """
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

@login_required
@check_permission
def dashboard(request):
    shop = request.user.shop

    # Получаем выбранный месяц из GET-запроса
    selected_month = request.GET.get('month')
    if selected_month:
        selected_year, selected_month = map(int, selected_month.split('-'))
    else:
        selected_year = now().year
        selected_month = now().month

    # Вычисляем текущие данные
    total_products = Product.objects.filter(shop=shop).count()
    total_expenses = Expense.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).aggregate(total=Sum('amount'))['total'] or 0
    total_incomes = IncomeHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).aggregate(total=Sum('amount'))['total'] or 0
    total_sales = SoldHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).aggregate(total=Sum('amount'))['total'] or 0

    # Вычисляем прибыль
    profit = total_sales - total_expenses

    # Вычисляем данные за предыдущий месяц
    previous_month = selected_month - 1 if selected_month > 1 else 12
    previous_year = selected_year if selected_month > 1 else selected_year - 1

    previous_expenses = Expense.objects.filter(shop=shop, created__year=previous_year, created__month=previous_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_incomes = IncomeHistory.objects.filter(shop=shop, created__year=previous_year, created__month=previous_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_sales = SoldHistory.objects.filter(shop=shop, created__year=previous_year, created__month=previous_month).aggregate(total=Sum('amount'))['total'] or 0

    # Вычисляем рост показателей
    def calculate_growth(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return ((current - previous) / previous) * 100

    expenses_growth = calculate_growth(total_expenses, previous_expenses)
    incomes_growth = calculate_growth(total_incomes, previous_incomes)
    sales_growth = calculate_growth(total_sales, previous_sales)

    # Топ продаж
    top_sold_products = SoldHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).values('product__name', 'product__unit').annotate(total_quantity=Sum('quantity'), total_amount=Sum('amount')).order_by('-total_quantity')[:5]

    context = {
        'shop': shop,
        'total_products': total_products,
        'total_expenses': total_expenses,
        'total_incomes': total_incomes,
        'total_sales': total_sales,
        'expenses_growth': expenses_growth,
        'incomes_growth': incomes_growth,
        'sales_growth': sales_growth,
        'top_sold_products': top_sold_products,
        'profit': profit,
        'current_month': f'{selected_month:02d}',
        'current_year': selected_year,
        'selected_month': f'{selected_year}-{selected_month:02d}'
    }

    return render(request, 'dashboard.html', context)



@login_required
@check_permission
def settings(request):
    user = request.user
    form = ShopForm(instance=user.shop)
    if request.method == 'POST':
        form = ShopForm(request.POST, instance=user.shop)
        if form.is_valid():
            form.save()
            return redirect('settings')

    shop = Shop.objects.get(id=request.user.shop.id)

    context = {
        'form': form,
        'shop': shop,
    }
    return render(request, 'settings.html', context)
