from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
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
from django.http import HttpResponse
from import_export.formats import base_formats
from .resources import ProductResource
import logging

logger = logging.getLogger(__name__)

@login_required
def update_per_pages(request):
    # Проверка для products_per_page
    if "products" in request.POST:
        number = request.POST.get('number_per_page')
        if number.isdigit() and int(number) > 0:
            request.user.shop.products_per_page = int(number)
            request.user.shop.save()
            return redirect('product-list')

    # Проверка для finance_per_page
    if "finance" in request.POST:
        number = request.POST.get('number_per_page')
        if number.isdigit() and int(number) > 0:
            request.user.shop.finance_per_page = int(number)
            request.user.shop.save()
            return redirect('finance-list')

    # Проверка для category_per_page
    if "category" in request.POST:
        number = request.POST.get('number_per_page')
        if number.isdigit() and int(number) > 0:
            request.user.shop.category_per_page = int(number)
            request.user.shop.save()
            return redirect('category-list')

    # Проверка для orderhistory_per_page
    if "orderhistory" in request.POST:
        number = request.POST.get('number_per_page')
        if number.isdigit() and int(number) > 0:
            request.user.shop.orderhistory_per_page = int(number)
            request.user.shop.save()
            return redirect('total')

    # Проверка для salehistory_per_page
    if "salehistory" in request.POST:
        number = request.POST.get('number_per_page')
        if number.isdigit() and int(number) > 0:
            request.user.shop.salehistory_per_page = int(number)
            request.user.shop.save()
            return redirect('sold-history')

    # Проверка для incomehistory_per_page
    if "incomehistory" in request.POST:
        number = request.POST.get('number_per_page')
        if number.isdigit() and int(number) > 0:
            request.user.shop.incomehistory_per_page = int(number)
            request.user.shop.save()
            return redirect('income-history')

    return redirect('dashboard')


@csrf_exempt
def select_all_products(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filter_params = data.get("filters", "")
            check_only = data.get("check_only", False)

            products = Product.objects.filter(shop=request.user.shop)
            
            if filter_params:
                filters = ProductFilter(request.GET, queryset=products, shop=request.user.shop)
                products = filters.qs

            selected_ids = [str(product.id) for product in products]

            if check_only:
                return JsonResponse({"success": True, "selected_ids": selected_ids})
            
            return JsonResponse({"success": True, "selected_ids": selected_ids})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False})


@csrf_exempt
def export_products(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_ids = data.get("product_ids", [])
            format_type = data.get("format", "csv")
            fields = data.get("fields", [])

            if not product_ids:
                return JsonResponse({"success": False, "error": "Нет выбранных товаров"}, status=400)

            if not fields:
                return JsonResponse({"success": False, "error": "Не выбраны поля для экспорта"}, status=400)

            # Фильтруем товары
            products = Product.objects.filter(id__in=product_ids, shop=request.user.shop)
            if not products.exists():
                return JsonResponse({"success": False, "error": "Товары не найдены"}, status=404)

            # Создаем ресурс
            resource = ProductResource()
            dataset = resource.export(queryset=products)

            # Фильтруем Dataset, оставляя только выбранные поля
            from tablib import Dataset
            filtered_dataset = Dataset()
            filtered_headers = [field.replace('category__name', 'category') for field in fields]
            filtered_dataset.headers = filtered_headers

            for row in dataset.dict:
                filtered_row = []
                for field in fields:
                    if field == 'category__name':
                        value = row.get('category', '')
                    else:
                        value = row.get(field, '')
                    filtered_row.append(str(value) if value is not None else '')
                filtered_dataset.append(filtered_row)

            # Выбор формата
            if format_type == "xlsx":
                format_obj = base_formats.XLSX()
                file_data = format_obj.export_data(filtered_dataset)
                filename = "exported_products.xlsx"
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:  # csv по умолчанию
                format_obj = base_formats.CSV()
                file_data = format_obj.export_data(filtered_dataset)
                filename = "exported_products.csv"
                content_type = "text/csv"

            response = HttpResponse(file_data, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            logger.error(f"Ошибка при экспорте: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Недопустимый метод"}, status=400)

@csrf_exempt
def delete_products(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_ids = data.get("product_ids", [])

            if not product_ids:
                return JsonResponse({"success": False, "error": "Нет выбранных товаров"}, status=400)

            products = Product.objects.filter(id__in=product_ids, shop=request.user.shop)
            count = products.count()
            products.delete()
            messages.success(request, 'Удалено товаров: ' + str(count))
            
            return JsonResponse({"success": True, "deleted_count": count})
        except Exception as e:
            logger.error(f"Ошибка при удалении: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Недопустимый метод"}, status=400)

@login_required
@check_permission
def list_(request):
   
    products = Product.objects.filter(shop=request.user.shop)
    products_count = products.count()
    categories = Category.objects.filter(shop=request.user.shop)
    query = request.GET.get('query', '').strip()
    number_per_page = request.user.shop.products_per_page

    filters = ProductFilter(request.GET, queryset=products, shop=request.user.shop)

    page_number = request.GET.get('page')

    page_obj, visible_pages = paginate(request, filters.qs, page_number, per_page=number_per_page)

    selected_ids = request.session.get('selected_products', [])

    context = {
        'categories': categories,
        'visible_pages': visible_pages,
        'page_obj': page_obj,
        'query': query,
        'filters': filters,
        'products_count':products_count,
        'selected_ids': selected_ids,
        'number_per_page':number_per_page
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
    number_per_page = request.user.shop.category_per_page

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.instance.shop = request.user.shop
            form.save()
            return redirect('category-list')

    # Пагинация
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, categories, page_number, number_per_page)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'form': form,
        'number_per_page':number_per_page
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