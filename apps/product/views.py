from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .tasks import import_products_from_csv
from django.contrib.auth.models import Permission
from django.core.paginator import Paginator
from celery.result import AsyncResult
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
from decimal import Decimal
from apps.history.models import *
from apps.finance.models import *
from .models import *
from .forms import *
import json
from .filters import ProductFilter
from .utils import paginate
from apps.user.utils import check_permission
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site




@login_required
@check_permission
def list_(request):
   
    products = Product.objects.filter(shop=request.user.shop)
    categories = Category.objects.filter(shop=request.user.shop)
    query = request.GET.get('query', '').strip()

    filters = ProductFilter(request.GET, queryset=products, shop=request.user.shop)

    page_number = request.GET.get('page')

    page_obj, visible_pages = paginate(request, filters.qs, page_number)


    context = {
        'categories': categories,
        'visible_pages': visible_pages,
        'page_obj': page_obj,
        'query': query,
        'filters': filters
    }
    return render(request, 'product/list.html', context)



def start_csv_import(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        if not csv_file:
            return JsonResponse({'error': 'Файл не был передан'}, status=400)

        try:
            task = import_products_from_csv.delay(csv_file.read().decode('utf-8'), request.user.shop.id)
            messages.success(request, 'Импорт успешно запущен!')
            return JsonResponse({'task_id': task.id})
        except Exception as e:
            messages.error(request, f'Ошибка запуска импорта: {e}')
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def check_csv_import_status(request):
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'Task ID is required'}, status=400)

    task = AsyncResult(task_id)
    if task.status == 'FAILURE':
        return JsonResponse({
            'status': task.status,
            'error': str(task.result)  # Возвращаем ошибку, если задача завершилась неудачно
        })

    return JsonResponse({
        'status': task.status,
        'progress': task.result.get('current') if task.result else None,
        'total': task.result.get('total') if task.result else None
    })

@login_required
@check_permission
def create(request):
  
    form = ProductForm(shop=request.user.shop)
    if request.method == 'POST':
        form = ProductForm(request.POST, shop=request.user.shop)
        if form.is_valid():
            form.instance.shop = request.user.shop
            form.save()
            messages.success(request, 'Товар успешно создан')
            return redirect('product-create')
        else:
            messages.error(request, 'Ошибка при создании товара')
    
    context = {
        'form': form,
    }
    
    return render(request, 'product/create.html', context)



@login_required
@check_permission
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

@login_required
@check_permission
def delete(request, pk):
   
    Product.objects.get(id=pk).delete()
    return redirect('product-list')

@login_required
def sale(request):
    return render(request, 'product/sale.html')


@login_required
def income_create(request, product_id, quantity, amount):
    product = Product.objects.get(id=product_id)
    product.quantity += int(quantity)
    product.save()
    
    order = OrderHistory.objects.create(
        shop=request.user.shop,
        amount=amount,
        change=0,
        order_type='income',
        user=request.user)

    IncomeHistory.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        shop=request.user.shop,
        amount=amount
    )


@login_required
def income(request):
    
    products = Product.objects.filter(shop=request.user.shop)
    categories = Category.objects.filter(shop=request.user.shop)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        amount = request.POST.get('amount')
        income_create(request, product_id, quantity, amount)
        return redirect('product-income')       


    filters = ProductFilter(request.GET, queryset=products, shop=request.user.shop)
    # Для пагинации
    page_number = request.GET.get('page')

    page_obj, visible_pages = paginate(request, filters.qs, page_number)


    context = {
        'categories': categories,
        'visible_pages': visible_pages,
        'page_obj': page_obj,
        'filters': filters
     }
    return render(request, 'product/income.html', context)

def generate_qr_code(order_id, request):
    """Генерирует QR-код для заказа с учётом текущего хоста"""
    current_site = get_current_site(request)
    qr_data = f"https://{current_site.domain}/history/receipt/{order_id}"  # Формируем полный URL

    qr = qrcode.make(qr_data)

    # Сохраняем QR-код в памяти
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)

    # Создаём файл для Django
    return ContentFile(qr_io.read(), name=f'qr_codes/order_{order_id}.png')


@login_required
@check_permission
def create_sale_history(request):
    
    if request.method == 'POST':
        products = json.loads(request.POST.get('products'))
        amount = request.POST.get('amount')
        change = request.POST.get('change')
        discount = request.POST.get('discount', 0)
        payment_method = request.POST.get('payment_method')
        profit = Decimal(0)
        order = OrderHistory.objects.create(
            shop=request.user.shop,
            amount=amount,
            change=change,
            discount=discount,
            order_type='sale',
            cashier=request.user,
            payment_method=payment_method
        )

        qr_code_file = generate_qr_code(order.id, request)
        order.qr_code.save(f'order_{order.id}.png', qr_code_file, save=True)

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
                amount=product.discounted_price(),
            )

            product_profit = (product.discounted_price() - product.cost_price) * quantity
            profit += product_profit


            # Обновляем количество продукта
            product.quantity -= quantity
            product.save()
        
        profit = profit - Decimal(discount)

        order.profit = profit
        order.save()


        return JsonResponse({'status': 'success','order_id': order.id })

        

@login_required
@check_permission
def category_list(request):

    categories = Category.objects.annotate(total_products=Count('product')).filter(shop=request.user.shop)
    form = CategoryForm()   

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.instance.shop = request.user.shop
            form.save()
            return redirect('category-list')

    # Пагинация
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, categories, page_number)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'form': form,
    }
    return render(request, 'product/category_list.html', context)

@login_required
@check_permission
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
@check_permission
def category_update(request, pk):
    
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