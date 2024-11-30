from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from apps.history.models import *
from apps.finance.models import *
from django.forms.models import model_to_dict
import json
from django.core.mail import send_mail
from django.utils.timezone import now
from apps.user.models import User
from backend import settings
from django.db.models import F


def check_inventory_levels(products):
    for item in products:
        product = Product.objects.get(id=item['id'])
        if product.quantity <= product.min_quantity:
            send_low_stock_notification(product)
            log_low_stock_notification(product)

def send_low_stock_notification(product):
    # Отправка email уведомления
    subject = f"Низкий уровень запасов: {product.name}"
    message = f"Количество товара  '{product.name}'  на складе ниже минимального порога. Остаток: {product.quantity}."
    from_email = settings.EMAIL_HOST_USER
    
    # Получаем всех пользователей, которым нужно отправить уведомление (например, администраторы или менеджеры)
    users = User.objects.filter(role='manager')  # или любые другие фильтры
    for user in users:
        if user.email:
            send_mail(subject, message, from_email, [user.email])
        else:
            print(f"Пользователь {user.username} не имеет электронной почты.")
    
    # Встроенные уведомления в системе (popup, push и т.д.)
    send_system_notification(product)

def send_system_notification(product):
    # Например, здесь будет код для отправки уведомления внутри системы.
    # Реализация зависит от используемого фронтенда (например, через Django Channels для WebSockets).
    notification_message = f"Низкий уровень запасов: {product.name}. Остаток: {product.quantity}."
    # Здесь можно интегрировать с фронтенд системой для показа уведомлений пользователям.

def log_low_stock_notification(product):
    # Логирование отправленных уведомлений
    LogEntry.objects.create(
        action="low_stock_notification",
        message=f"Товар: {product.name}, остаток: {product.quantity}",
        created_at=now()
    )


def list_(request):
    search_query = request.GET.get('search', '')

    if search_query:
        products = Product.objects.filter(name__icontains=search_query, shop=request.user.shop)
    else:
        products = Product.objects.filter(shop=request.user.shop)
    
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

    context = {
        'products': products
    }
    return render(request, 'product/list.html', context)


def create(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.shop = request.user.shop
            form.save()
            messages.success(request, 'Товар успешно создан')
            return redirect('product-create')
        else:
            messages.error(request, 'Ошибка при создании товара')
    return render(request, 'product/create.html', {'form': form})

def product_create(request):
    # Проверяем, что запрос является AJAX и имеет метод POST
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Преобразуем данные JSON из запроса
        data = json.loads(request.body)
        
        # Создаем объект Product с полученными данными и значениями по умолчанию
        product = Product(
            name=data.get('name'),
            bar_code=data.get('barcode'),
            price=data.get('price', 0),       # Цена по умолчанию 0
            quantity=data.get('quantity', 0), # Количество по умолчанию 0
            sale_price=data.get('sale_price', 0), # Продажная цена по умолчанию 0
            shop=request.user.shop
        )

        # Сохраняем объект и возвращаем ответ JSON
        try:
            product.save()
            return JsonResponse({'success': True, 'barcode': product.bar_code})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def details(request, pk):
    product = Product.objects.get(id=pk)

    context = {
        'product': product,
    }
    return render(request, 'product/details.html', context)


def update(request, pk):
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


def delete(request, pk):
    Product.objects.get(id=pk).delete()
    return redirect('product-list')


def sale(request):
    return render(request, 'product/sale.html')

def income(request):
    return render(request, 'product/income.html')


def get_product(request):
    bar_code = request.GET.get('bar_code')
    product = get_object_or_404(Product, bar_code=bar_code)

    product = {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'sale_price': product.sale_price,
        'bar_code': product.bar_code,
        'quantity': product.quantity,
        'status': 'success' if product is not None else 'error',
    }

    return JsonResponse(product, safe=False)


def create_sell_history(request):
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
                price_at_moment=product.sale_price  # Сохраняем цену на момент продажи
            )

            product_profit = (Decimal(product.sale_price) - Decimal(product.price)) * quantity
            profit += product_profit


            # Обновляем количество продукта
            product.quantity -= quantity
            product.save()
        
        profit = profit - Decimal(discount)

        order.profit = profit
        order.save()

        check_inventory_levels(products)

        return JsonResponse({'status': 'success'})
        

def create_income_history(request):
    if request.method == 'POST':
        products = json.loads(request.POST.get('products'))
        amount = request.POST.get('amount')
        change = request.POST.get('change')

        # Создаем запись о поступлении
        order = OrderHistory.objects.create(
            amount=amount,
            change=change,
            shop=request.user.shop
        )
        expend = Expense.objects.create(
            expend_type='supplies',
            description='Поступление',
            amount=amount,
            shop=request.user.shop,
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
                price_at_moment=price
            )

            # Обновляем количество и цены продукта
            product.quantity += quantity
            product.price = price  # Обновляем цену
            product.sale_price = sale_price  # Обновляем продажную цену
            product.save()

        return JsonResponse({'status': 'success'})


def update_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        product = Product.objects.get(id=product_id)
        product.quantity = quantity
        product.save()

        return JsonResponse({'status': 'success'})


def find_product(request):
    barcode = request.GET.get('barcode')
    try:
        product = Product.objects.get(bar_code=barcode, shop=request.user.shop)
        return JsonResponse({'product_name': product.name, 'price': product.price, 'image': product.image.url})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


def search_product(request):
    query = request.GET.get('query', '')
    products = Product.objects.filter(name__icontains=query).values('bar_code', 'name', 'quantity')
    return JsonResponse(list(products), safe=False)


def low_stock(request):
    products = Product.objects.filter(quantity__lte=F('min_quantity'), shop=request.user.shop)
    return render(request, 'product/low_stock.html', {'products': products})