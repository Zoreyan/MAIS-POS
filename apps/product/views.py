from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from apps.history.models import *
from apps.finance.models import *
from django.forms.models import model_to_dict
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q, Case, When, IntegerField
from django.db import IntegrityError
from django.contrib.auth.models import Permission
from .tasks import check_product_stock
from decimal import Decimal
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile





@login_required
def update_product_per_page(request):
    if request.method == "POST":
        try:
            items_per_page = int(request.POST.get("items_per_page", 10))
            if items_per_page > 0:
                request.session['items_per_page'] = items_per_page
        except ValueError:
            request.session['items_per_page'] = 10  # Устанавливаем значение по умолчанию
    return redirect('product-list') 

@login_required
def list_(request):
    permission = Permission.objects.filter(user=request.user, codename='view_product')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)
        return redirect('dashboard')

    products = Product.objects.filter(shop=request.user.shop)

    categories = Category.objects.filter(shop=request.user.shop)

    query = request.GET.get('query', '').strip()

    if query:
        if query.isdigit():
            products = products.filter(shop=request.user.shop, bar_code__icontains=query)
        else:
            products = products.filter(
                Q(shop=request.user.shop) & 
                (Q(name__icontains=query) | Q(category__name__icontains=query))
            )         
    # Фильтр по категории и родительской категории
    selected_category = request.GET.get('category')
    if selected_category:
        # Получаем выбранную категорию
        category = Category.objects.filter(name=selected_category, shop=request.user.shop).first()

        # Продукты из выбранной категории
        category_products = products.filter(category=category)

        # Продукты из дочерних категорий
        child_categories = category.children.all() if category else []
        child_category_products = products.filter(category__in=child_categories)

        # Объединяем и сортируем продукты
        products = list(category_products) + list(child_category_products)

    # Фильтр по минимальной сумме
    price_min = request.GET.get('price_min')
    if price_min:
        products = products.filter(price__gte=price_min)

    # Фильтр по максимальной сумме
    price_max = request.GET.get('price_max')
    if price_max:
        products = products.filter(price__lte=price_max)

    # Фильтр по наличию
    in_stock = request.GET.get('in_stock')
    if in_stock == "yes":
        products = products.filter(quantity__gt=0)
    elif in_stock == "no":
        products = products.filter(quantity=0)
    elif in_stock == "low":
        produkts = []
        for product in products:
            if product.min_quantity:
                produkts.append(product)
        products = produkts

    # Фильтр по наличию
    discount = request.GET.get('discount')
    if discount == "yes":
        products = products.filter(discount__gt=0)
    elif discount == "no":
        products = products.filter(discount=0)

    # Для пагинации
    items_per_page = request.session.get('items_per_page', 10)
    paginator = Paginator(products, items_per_page)
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
        'categories': categories,
        'visible_pages': visible_pages,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'product/list.html', context)

@login_required
def create(request):
    products_count = Product.objects.filter(shop=request.user.shop).count()
    tariff = request.user.shop.tariff
    limit = 0
    max_products = 0

    if tariff:
        product_limit = tariff.features.filter(name__icontains="товара").first()
        
        if product_limit:
            list_max = []
            pr_limit = str(product_limit)
            
            if '∞' in pr_limit:
                # Устанавливаем бесконечное количество товаров
                max_products = float('inf')
                limit = '∞'
            else:
                try:
                    for i in pr_limit:
                        if i.isdigit():
                            list_max.append(i)
                    # Если найдены цифры, преобразуем их в число
                    if list_max:
                        max_products = int(''.join(list_max))
                        limit = max_products - products_count
                    else:
                        raise ValueError("Не удалось найти число в строке product_limit.")
                except:
                    max_products = float('inf')
                    limit = '∞'
    
    permission = Permission.objects.filter(user=request.user, codename='add_product')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)

        return redirect('dashboard')

    form = ProductForm()
    if request.method == 'POST':
        if products_count >= max_products:
            messages.error(request, 'Превышено количество товаров')
            return redirect('product-create')
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.shop = request.user.shop
            form.save()
            messages.success(request, 'Товар успешно создан')
            return redirect('product-create')
        else:
            messages.error(request, 'Ошибка при создании товара')
    
    context = {
        'form': form,
        'limit': limit
    }
    
    return render(request, 'product/create.html', context)

@login_required
def details(request, pk):
    product = Product.objects.get(id=pk)

    context = {
        'product': product,
    }
    return render(request, 'product/details.html', context)

@login_required
def update(request, pk):
    permission = Permission.objects.filter(user=request.user, codename='change_product')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)
        return redirect('dashboard')

    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product-list')

    context = {
        'product': product,
        'form': form
    }
    return render(request, 'product/update.html', context)

@login_required
def delete(request, pk):
    permission = Permission.objects.filter(user=request.user, codename='delete_product')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)
        return redirect('dashboard')

    Product.objects.get(id=pk).delete()
    return redirect('product-list')

@login_required
def sale(request):
    return render(request, 'product/sale.html')
@login_required
def income(request):
    return render(request, 'product/income.html')

@login_required
def get_product(request):
    bar_code = request.GET.get('bar_code')
    product_id = request.GET.get('id')
    print(bar_code)
    if bar_code:
        product = get_object_or_404(Product, bar_code=bar_code, shop=request.user.shop)  # Находим продукт по штрихкоду
    elif product_id:
        product = get_object_or_404(Product, id=product_id, shop=request.user.shop)  # Находим продукт по ID
    else:
        return JsonResponse({'status': 'error', 'message': 'Штрихкод или ID не переданы'}, status=400)
    
    sale_price = product.discounted_price()
    product_data = {
        'id': product.id,  # Возвращаем ID продукта
        'name': product.name,
        'price': product.price,
        'sale_price': product.sale_price,
        'd_sale_price':sale_price,
        'bar_code': product.bar_code,
        'quantity': product.quantity,
        'image': product.image.url if product.image else None,  # Поле для изображения
        'status': 'success'
    }
    return JsonResponse(product_data)

@login_required
def create_sell_history(request):
    if not request.user.shop.is_active:
        return redirect('dashboard')

    if request.method == 'POST':
        products = json.loads(request.POST.get('products'))
        amount = request.POST.get('amount')
        change = request.POST.get('change')
        discount = request.POST.get('discount')

        profit = Decimal(0)

        if discount == '':
            discount = 0

        order = OrderHistory.objects.create(
            shop=request.user.shop,
            amount=amount,
            change=change,
            discount=discount,
            order_type='sale'
        )
        for item in products:
            product = Product.objects.get(id=item['id'])
            quantity = int(item['quantity'])

            # Проверяем доступность количества
            if product.quantity < quantity:
                return JsonResponse({
                    'status': 'error',
                    'message': f"Недостаточно товара для продукта {product.name}. Доступно: {product.quantity}, запрошено: {quantity}."
                })

            # Сохраняем текущую цену продукта
            SoldHistory.objects.create(
                shop=request.user.shop,
                order=order,
                product=product,
                quantity=quantity,
                price_at_moment=product.discounted_price(),
            )

            product_profit = (product.discounted_price() - product.price) * quantity
            profit += product_profit


            # Обновляем количество продукта
            product.quantity -= quantity
            product.save()
        
        profit = profit - Decimal(discount)

        order.profit = profit
        order.save()

        check_product_stock.delay(products, request.user.shop.id )

        return JsonResponse({'status': 'success'})
        
        
@login_required
def create_income_history(request):
    if not request.user.shop.is_active:
        return redirect('dashboard')
        
    if request.method == 'POST':
        products = json.loads(request.POST.get('products'))
        amount = request.POST.get('amount')
        change = request.POST.get('change')
        change = request.POST.get('change')

        # Создаем запись о поступлении
        order = OrderHistory.objects.create(
            amount=amount,
            change=change,
            shop=request.user.shop,
            order_type='income'
        )
        expend = Expense.objects.create(
            expend_type='supplies',
            description='Поступление',
            amount=amount,
            shop=request.user.shop
        )

        for item in products:
            product = Product.objects.get(id=item['id'])
            quantity = int(item['quantity'])
            price = float(item['price'])  # Получаем цену продукта из запроса
            sale_price = float(item['sale_price'])  # Получаем продажную цену из запроса

            
            IncomeHistory.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_moment=price,
                shop=request.user.shop
            )

            # Обновляем количество и цены продукта
            product.quantity += quantity
            product.price = price  # Обновляем цену
            product.sale_price = sale_price  # Обновляем продажную цену
            product.save()

        return JsonResponse({'status': 'success'})

@login_required
def update_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        product = Product.objects.get(id=product_id)
        product.quantity = quantity
        product.save()

        return JsonResponse({'status': 'success'})

@login_required
def find_product(request):
    barcode = request.GET.get('barcode')
    try:
        product = Product.objects.get(bar_code=barcode, shop=request.user.shop)
        return JsonResponse({'product_name': product.name, 'price': product.price, 'image': product.image.url})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

@login_required
def search_product(request):
    query = request.GET.get('query', '')
    products = []

    if query:
        print(query)
        if query.isdigit():
            products = Product.objects.filter(shop=request.user.shop, bar_code__icontains=query)
        else:
            products = Product.objects.filter(
                Q(shop=request.user.shop) & 
                (Q(name__icontains=query) | Q(category__name__icontains=query))
            )
    serialized_products = list(products.values())

    return JsonResponse({'products': serialized_products})

@login_required
def category_list(request):
    permission = Permission.objects.filter(user=request.user, codename='view_category')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)
        return redirect('dashboard')

    categories = Category.objects.annotate(total_products=Count('product')).filter(shop=request.user.shop)
    form = CategoryForm(shop=request.user.shop)   

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.instance.shop = request.user.shop
            form.save()
            return redirect('category-list')

    # Пагинация
    category_per_page = request.session.get('category_per_page', 10)
    paginator = Paginator(categories, category_per_page)
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
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'form': form,
    }
    return render(request, 'product/category_list.html', context)

@login_required
def update_category_per_page(request):
    if request.method == "POST":
        try:
            category_per_page = int(request.POST.get("category_per_page", 10))
            if category_per_page > 0:
                request.session['category_per_page'] = category_per_page
        except ValueError:
            request.session['category_per_page'] = 10
    return redirect('category-list')


@login_required
def category_delete(request, pk):
    permission = Permission.objects.filter(user=request.user, codename='delete_category')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)
        return redirect('dashboard')

    category = Category.objects.get(id=pk)
    category.delete()
    return redirect('category-list')

@login_required
def category_update(request, pk):
    permission = Permission.objects.filter(user=request.user, codename='change_category')
    if not permission.exists():
        referer = request.META.get('HTTP_REFERER')  # Получить URL предыдущей страницы
        if referer:  # Если заголовок HTTP_REFERER доступен
            return redirect(referer)
        return redirect('dashboard')

    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(instance=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category-list')

    context = {
        'category': category,
        'form': form
    }
    return render(request, 'product/category_update.html', context)