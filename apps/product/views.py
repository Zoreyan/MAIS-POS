from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .tasks import import_products_from_csv
from celery.result import AsyncResult
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
from .filters import ProductFilter
from apps.dashboard.utils import *
from apps.history.models import *
from apps.finance.models import *
from apps.utils.utils import *
from .models import *
from .forms import *
from .utils import *
import json



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
        try:

            if form.is_valid():
                form.instance.shop = request.user.shop
                form.save()
                LogHistory.objects.create(user=request.user, shop=request.user.shop, message='Добавлен товар', object=form.instance.name)
                messages.success(request, 'Товар успешно создан')

                return redirect('product-create')
            else:
                messages.error(request, 'Ошибка при создании товара')
        except Exception as e:
            messages.error(request, f'Ошибка уникальности баркода')
    context = {
        'form': form,
    }
    
    return render(request, 'product/create.html', context)


@login_required
@check_permission
def update(request, pk):
   
    product = get_object_or_404(Product, id=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            LogHistory.objects.create(user=request.user, message='Обновлен товар', shop=request.user.shop, object=form.instance.name)
            messages.success(request, 'Товар обновлен')
            return redirect('product-list')

    context = {
        'product': product,
        'form': form
    }
    return render(request, 'product/update.html', context)


@login_required
@check_permission
def delete(request, pk):
    delete_obj(request, Product, pk, 'Удален товар')
    return redirect('product-list')

@login_required
def sale(request):
    return render(request, 'product/sale.html')


@login_required
def income_create(request, product_id, quantity, amount):
    product = get_object_or_404(Product, id=product_id)
    product.quantity += int(quantity)
    product.save()
    

    IncomeHistory.objects.create(
        product=product,
        quantity=quantity,
        shop=request.user.shop,
        amount=amount
    )
    LogHistory.objects.create(user=request.user, shop=request.user.shop, message='Добавлена поставка')



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


@login_required
@check_permission
def create_sale_history(request):
    
    if request.method == 'POST':
        products = json.loads(request.POST.get('products'))
        cash_payment = int(request.POST.get('cash_payment', 0) or 0)
        online_payment = int(request.POST.get('online_payment', 0) or 0)
        change = int(request.POST.get('change', 0) or 0)
        discount = int(request.POST.get('discount', 0) or 0)
        
        
        order = create_sale(request, products=products,
                    cash_payment=cash_payment, online_payment=online_payment,
                    change=change, discount=discount)
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
    delete_obj(request, Category, pk, 'Удалена категория')
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
            LogHistory.objects.create(user=request.user, message='Обновлена категория', shop=request.user.shop, object=form.instance.name)
            return redirect('category-list')

    context = {
        'category': category,
        'form': form
    }
    return render(request, 'product/category_update.html', context)

@login_required
def get_product_chart_data(request):
    product_id = request.GET.get('product_id')
    print(product_id)
    sales_by_month = get_sales_by_month(request, SoldHistory, product__id=product_id)
    months = [sale['month'].strftime('%Y-%m') for sale in sales_by_month]  # Форматируем даты
    totals = [sale['total_sales'] for sale in sales_by_month]  # Суммы продаж

    return JsonResponse({'months': months, 'totals': totals})

def details(request, pk):
    product = get_object_or_404(Product, id=pk)
    total_sold_quantity = SoldHistory.objects.filter(product=product).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    context = {
        'product': product,
        'total_sold_quantity': total_sold_quantity
    }
    return render(request, 'product/details.html', context)