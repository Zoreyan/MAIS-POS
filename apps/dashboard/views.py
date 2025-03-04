from django.shortcuts import render, redirect
from .models import *
from apps.history.models import *
from django.db.models import Sum
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.product.models import Shop
from apps.history.models import *
from django.utils.timezone import now
from apps.user.utils import check_permission
from .utils import *



@login_required
def get_chart_data(request):
    sales_by_month = get_sales_by_month(request)
    months = [sale['month'].strftime('%Y-%m') for sale in sales_by_month]  # Форматируем даты
    totals = [sale['total_sales'] for sale in sales_by_month]  # Суммы продаж

    return JsonResponse({'months': months, 'totals': totals})



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
    total_products, total_expenses, total_incomes, total_sales, product_profit, total_sales_quantity = get_totals(request, shop, selected_year, selected_month)

    # Вычисляем предыдущие данные
    previous_expenses, previous_incomes, previous_sales, previous_sales_quantity = get_previous_totals(request, shop, selected_year, selected_month)

    # Вычисляем прибыль
    profit = product_profit - (total_expenses + total_incomes)

    # Вычисляем рост показателей
    expenses_growth, incomes_growth, sales_growth, sales_quantity_growth = get_growth_calculations(request, total_expenses=total_expenses, total_incomes=total_incomes, total_sales=total_sales, total_sales_quantity=total_sales_quantity, previous_expenses=previous_expenses, previous_incomes=previous_incomes, previous_sales=previous_sales, previous_sales_quantity=previous_sales_quantity)

    # Топ продаж
    top_sold_products = SoldHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).annotate(total_quantity=Sum('quantity'), total_amount=Sum('amount') * Sum('quantity')).order_by('-total_quantity')[:5]

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
        'total_sales_quantity': total_sales_quantity,
        'sales_quantity_growth': sales_quantity_growth,
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
