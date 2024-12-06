from django.shortcuts import render, redirect
from apps.product.models import Shop, Product
from django.core.paginator import Paginator


def update_shop_per_page(request):
    if request.method == "POST":
        try:
            shop_per_page = int(request.POST.get("shop_per_page", 10))
            if shop_per_page > 0:
                request.session['shop_per_page'] = shop_per_page
        except ValueError:
            request.session['shop_per_page'] = 10
    return redirect('settings')

def index(request, pk):
    shop = Shop.objects.get(id=pk)
    products = Product.objects.filter(shop=shop)

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
        'shop':shop,
        'page_obj':page_obj,
        'visible_pages': visible_pages,
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