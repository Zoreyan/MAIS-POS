from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from folium import Map, Marker

from apps.product.models import Shop, Product, Category
from .forms import ShopForm

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