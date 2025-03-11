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
from apps.utils.utils import check_permission
from .utils import *



@login_required
def get_chart_data(request):
    sales_by_month = get_sales_by_month(SoldHistory)
    months = [sale['month'].strftime('%Y-%m') for sale in sales_by_month]  # Форматируем даты
    totals = [sale['total_sales'] for sale in sales_by_month]  # Суммы продаж

    return JsonResponse({'months': months, 'totals': totals})




def parse_selected_month(request):
    """Обрабатывает выбранный месяц из GET-запроса"""
    selected_month = request.GET.get('month')
    if selected_month:
        try:
            selected_year, selected_month = map(int, selected_month.split('-'))
        except ValueError:
            selected_year, selected_month = now().year, now().month
    else:
        selected_year, selected_month = now().year, now().month
    return selected_year, selected_month

@login_required
@check_permission
def dashboard(request):
    shop = request.user.shop
    selected_year, selected_month = parse_selected_month(request)

    # Вычисляем текущие и предыдущие данные
    totals = get_totals(shop, selected_year, selected_month)
    previous_totals = get_previous_totals(shop, selected_year, selected_month)
    today_data = get_today(request)

    # Вычисляем прибыль
    profit = totals["profit"] - (totals["total_expenses"] + totals["total_incomes"])
    today_profit = today_data["product_profit"] - (today_data["today_expenses"] + today_data["today_incomes"])

    # Вычисляем рост показателей
    growth = get_growth_calculations(
        total_expenses=totals["total_expenses"], previous_expenses=previous_totals["previous_expenses"],
        total_incomes=totals["total_incomes"], previous_incomes=previous_totals["previous_incomes"],
        total_sales=totals["total_sales"], previous_sales=previous_totals["previous_sales"],
        total_sales_quantity=totals["sales_quantity"], previous_sales_quantity=previous_totals["previous_sales_quantity"],
    )

    # Топ-5 проданных товаров
    top_sold_products = SoldHistory.objects.filter(
        shop=shop, created__year=selected_year, created__month=selected_month
    ).annotate(
        total_quantity=Sum('quantity'), total_amount=Sum('amount') * Sum('quantity')
    ).order_by('-total_quantity')[:5]
    print(today_data.items())
    context = {
        "shop": shop,
        "profit": profit,
        "today_profit": today_profit,
        "top_sold_products": top_sold_products,
        "current_month": f"{selected_month:02d}",
        "current_year": selected_year,
        "selected_month": f"{selected_year}-{selected_month:02d}",
        **totals,  # Распаковка total_* переменных
        **previous_totals,  # previous_* переменные
        **today_data,  # today_* переменные
        **growth,  # growth_* переменные
    }

    return render(request, "dashboard.html", context)



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
