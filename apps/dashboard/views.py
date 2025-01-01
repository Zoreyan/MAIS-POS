from django.shortcuts import render, redirect
from .models import *
from apps.history.models import *
from django.db.models import Sum, F, Avg
import json
from .forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from apps.product.models import Shop, Product
from datetime import datetime
from apps.product.forms import ShopForm
import folium
from folium import Map, Marker
from apps.history.models import *

@login_required
def get_top_products_data(request):
    top_products = SoldHistory.objects.filter(shop=request.user.shop).values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    product_names = [item['product__name'] for item in top_products]
    product_sales = [item['total_quantity'] for item in top_products]

    return JsonResponse({
        'product_names': product_names,
        'product_sales': product_sales
    })

@login_required
def get_top_incomes_data(request):
    top_incomes = IncomeHistory.objects.filter(shop=request.user.shop).values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    product_names = [item['product__name'] for item in top_incomes]
    product_incomes = [item['total_quantity'] for item in top_incomes]
    
    return JsonResponse({
        'product_names': product_names,
        'product_incomes': product_incomes
    })

# График прибыли по месяцам
@login_required
def get_chart_data(request):
    # Получаем данные по продажам, агрегированные по месяцам
    sales_data = OrderHistory.objects.values('created__month').annotate(total_sales=Sum('profit')).order_by('created__month')
    
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    
    # Инициализация списка прибыли с нулями
    profit = [0] * 12
    
    # Заполнение данных по месяцам
    for sale in sales_data:
        month_index = sale['created__month'] - 1
        profit[month_index] = sale['total_sales']  # Используем суммарную продажу для месяца

    # Возвращаем данные в формате JSON
    return JsonResponse({
        'months': months,
        'profit': profit
    })

# Средняя цена поставок


@login_required
def dashboard(request):
    total_profit = SoldHistory.objects.filter().aggregate(profit=Sum('quantity'))['profit'] or 0
    total_income = IncomeHistory.objects.filter().aggregate(income=Sum('quantity'))['income'] or 0
    total_revenue = Product.objects.filter().aggregate(revenue=Sum('price'))['revenue'] or 0
    # Дополнительные данные для расчета роста
    growth = round((total_profit - total_income) / total_income * 100, 3) if total_income else 0
    sold_products = Product.objects.filter(shop=request.user.shop).annotate(total_quantity=Sum('soldhistory__quantity'), total_sum=Sum('soldhistory__quantity') * F('sale_price')).order_by('-total_quantity')[:5]
    context = {
        'sold_products': sold_products,
        'total_profit': total_profit,
        'total_income': total_income,
        'total_revenue': total_revenue,
        'growth': growth
    } 
    return render(request, 'dashboard.html', context)


@login_required
def settings_page(request):
    user = request.user
    form = ShopForm(instance=user.shop)
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=user.shop)
        if form.is_valid():
            form.save()
            return redirect('settings')


    # Получаем объект магазина
    shop = Shop.objects.get(id=request.user.shop.id) if request.user.shop else None
    coordinates = shop.coordinates if shop else None

    # Проверяем наличие координат
    if coordinates:
        try:
            lat, lon = map(float, coordinates.split(','))  # Разбиваем и конвертируем координаты
            map_center = [lat, lon]  # Устанавливаем центр карты на координаты магазина
            m = Map(location=map_center, zoom_start=8)

            # Создаём карту с центром на координаты магазина или по умолчанию
    

            map_html = m._repr_html_()

            # Если у магазина есть координаты, добавляем маркер
            if coordinates:
                Marker(location=[lat, lon]).add_to(m)
        except ValueError:
            map_center = [40.516018, 72.803835]  # Центр по умолчанию
            map_html = Map(location=map_center, zoom_start=8)._repr_html_()
    else:
        map_center = [40.516018, 72.803835]  # Центр по умолчанию

    context = {
        'form': form,
        'map_html': map_html,
        'shop': shop,
    }
    return render(request, 'settings_page.html', context)