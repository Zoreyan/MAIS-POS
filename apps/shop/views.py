from django.shortcuts import render, redirect, get_object_or_404
from apps.product.models import Shop, Product, Category
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import ShopForm
from apps.dashboard.models import *
from django.contrib import messages
import folium
from folium import Map, Marker
from django.http import JsonResponse
import json
import re
from datetime import timedelta 
from django.utils import timezone 
from django.utils.timezone import now




def update_shop_per_page(request):
    if request.method == "POST":
        try:
            shop_per_page = int(request.POST.get("shop_per_page", 10))
            if shop_per_page > 0:
                request.session['shop_per_page'] = shop_per_page
        except ValueError:
            request.session['shop_per_page'] = 10
    return redirect('shop-index', pk=request.POST.get('shop_id'))

def index(request, pk):
    shop = Shop.objects.get(id=pk)
    products = Product.objects.filter(shop=shop)
    query = request.GET.get('query', '').strip()
    
    categories = Category.objects.filter(parent__isnull=True)
    category_childs = Category.objects.all()

    for category in categories:
        category_children = category_childs.filter(parent=category)

    if query:
        if query.isdigit():
            products = products.filter(shop=shop, bar_code__icontains=query)
        else:
            products = products.filter(
                Q(shop=shop) & 
                (Q(name__icontains=query) | Q(category__name__icontains=query))
            )

    # Пагинация и другие данные
    shop_per_page = request.session.get('shop_per_page', 10)
    paginator = Paginator(products, shop_per_page)
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
        'shop': shop,
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'query': query,
        'categories': categories,
        'category_children': category_children,
    }
    return render(request, 'shop/index.html', context)


def about_us(request, pk):
    shop = Shop.objects.get(id=pk)
    context = {
        'shop': shop
    }
    return render(request, 'shop/about_us.html', context)


def contacts(request, pk):
    shop = Shop.objects.get(id=pk)
    context = {
        'shop': shop
    }
    return render(request, 'shop/contacts.html', context)


def vacancies(request, pk):
    shop = Shop.objects.get(id=pk)
    context = {
        'shop': shop
    }
    return render(request, 'shop/vacancies.html', context)


def order_list(request):
    context = {
    }
    return render(request, 'shop/order_list.html', context)


@login_required
def settings(request):
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
        map_html = Map(location=map_center, zoom_start=8)._repr_html_()

    context = {
        'form': form,
        'map_html': map_html,
        'shop': shop,
    }
    return render(request, 'shop/settings.html', context)

def management(request, pk):
    shop = Shop.objects.get(id=pk)
    tariffs = Tariff.objects.all()
    tariff_features_dict = {}
    payment_periods = PaymentPeriod.objects.all().order_by('duration')
    payment_history = Payment.objects.filter(shop=shop).order_by('-payment_date')

    if shop.tariff:
        sellected_tariff = shop.tariff.id
        current_tariff = shop.tariff
        current_tariff_features = current_tariff.features.order_by('sequence', 'id')
    else:
        current_tariff = None
        sellected_tariff = None
        current_tariff_features = None

    for tariff in tariffs:
        tariff_features = tariff.features.order_by('sequence', 'id')
        tariff_features_dict[tariff] = tariff_features

    context = {
        'shop': shop,
        'tariffs':tariffs,
        'tariff_features_dict': tariff_features_dict,
        'sellected_tariff': sellected_tariff,
        'current_tariff': current_tariff,
        'current_tariff_features':current_tariff_features,
        'payment_periods': payment_periods,
        'payment_history': payment_history,
    }
    return render(request, 'shop/management.html', context)



def process_payment(request, shop_id):
    if request.method != 'POST':
        messages.error(request, "Неверный метод запроса.")
        return redirect('dashboard')

    # Получаем магазин по ID
    shop = get_object_or_404(Shop, id=shop_id)

    # Получаем текущий тариф
    current_tariff = shop.tariff

    # Получаем данные из POST-запроса
    tariff_id = request.POST.get('tariff', current_tariff.id)
    period_id = request.POST.get('payment_period')

    # Получаем тариф и период
    tariff = get_object_or_404(Tariff, id=tariff_id)
    period = get_object_or_404(PaymentPeriod, id=period_id)
    

    # Рассчитываем сумму тарифа
    tariff_price = tariff.price / 30
    total_amount = tariff_price * period.duration  # Сумма без скидки
    discount = period.discount / 100 if period.discount else 0  # Скидка в процентах
    discounted_amount = total_amount * (1 - discount)

    # Проверяем баланс
    if shop.balance < discounted_amount:
        messages.error(request, "Недостаточно средств для оплаты.")
        return redirect('management', shop.id)

    # Проверяем количество товаров и ограничения тарифа
    if current_tariff != tariff:
        product_limit = tariff.features.filter(name__icontains="товара").first()
        
        if product_limit:
            list_max = []
            pr_limit = str(product_limit)
            
            if '∞' in pr_limit:
                # Устанавливаем бесконечное количество товаров
                max_products = float('inf')
            else:
                # Извлекаем только цифры из строки
                for i in pr_limit:
                    if i.isdigit():
                        list_max.append(i)
                # Если найдены цифры, преобразуем их в число
                if list_max:
                    max_products = int(''.join(list_max))
                else:
                    raise ValueError("Не удалось найти число в строке product_limit.")
            
            # Преобразуем значение sequence в число
            try:
            
                # Проверяем количество товаров в магазине
                current_product_count = Product.objects.filter(shop=shop).count()
                print("Текущее количество товаров в магазине:", current_product_count)

                if current_product_count > max_products:
                    messages.error(
                        request,
                        f"Переход на тариф невозможен. Снизьте количество товаров до {max_products} для перехода на данный тариф."
                    )
                    return redirect('management', shop.id)
            except ValueError:
                print("Не удалось преобразовать значение sequence в число.")
        else:
            print("Поле product_limit не найдено.")

    # Создаем запись оплаты
    Payment.objects.create(
        shop=shop,
        tariff=tariff,
        period=period,
        amount=discounted_amount,
    )

    # Обновляем баланс и срок действия тарифа
    shop.balance -= discounted_amount
    if current_tariff != tariff:
        shop.tariff = tariff
        shop.payment_due_date = now() + timedelta(days=period.duration)
    else:
        shop.payment_due_date = (shop.payment_due_date or now()) + timedelta(days=period.duration)
    
    shop.payment_due_date = shop.payment_due_date.replace(minute=59, second=0, microsecond=0)
    shop.is_active = True
    shop.save()

    # Сообщение об успешной оплате
    messages.success(request, "Оплата успешно произведена.")
    return redirect('management', shop.id)

def update_auto_pay(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            auto_pay = data.get('auto_pay')

            shop = request.user.shop
            shop.auto_pay = auto_pay
            shop.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})