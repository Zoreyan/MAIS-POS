from .filters import OrderHistoryFilter, SoldHistoryFilter, IncomeHistoryFilter, LogHistoryFilter
from django.db.models import Q, Sum, F
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.utils.utils import paginate
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from .models import *
from import_export import resources
from import_export.formats import base_formats
from django.contrib import messages
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def select_all_orders(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filter_params = data.get("filters", "")
            check_only = data.get("check_only", False)

            # Фильтруем заказы по магазину пользователя
            orders = OrderHistory.objects.filter(shop=request.user.shop)
            
            if filter_params:
                # Предполагается, что у вас есть OrderFilter, аналогичный ProductFilter
                filters = OrderHistoryFilter(request.GET, queryset=orders, shop=request.user.shop)
                orders = filters.qs

            selected_ids = [str(order.id) for order in orders]

            if check_only:
                return JsonResponse({"success": True, "selected_ids": selected_ids})
            
            return JsonResponse({"success": True, "selected_ids": selected_ids})
        except Exception as e:
            logger.error(f"Ошибка при выборе всех заказов: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "Недопустимый метод"}, status=400)


@csrf_exempt
def export_orders(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_ids = data.get("order_ids", [])
            format_type = data.get("format", "csv")

            if not order_ids:
                return JsonResponse({"success": False, "error": "Нет выбранных заказов"}, status=400)

            # Фильтруем заказы
            orders = OrderHistory.objects.filter(id__in=order_ids, shop=request.user.shop)
            if not orders.exists():
                return JsonResponse({"success": False, "error": "Заказы не найдены"}, status=404)

            # Создаем ресурс для экспорта заказов
            class OrderResource(resources.ModelResource):
                class Meta:
                    model = OrderHistory
                    fields = (
                        'user', 'cash_payment', 'online_payment', 
                        'change', 'discount', 'payment_method', 
                        'created'
                    )
                    export_order = fields

                def dehydrate_user__first_name(self, order):
                    return order.user.first_name if order.user.first_name else str(order.user.id)

                def dehydrate_payment_method(self, order):
                    return order.get_payment_method_display()

                def dehydrate_created(self, order):
                    return order.created.strftime('%d.%m.%Y %H:%M')

            resource = OrderResource()
            dataset = resource.export(queryset=orders)

            # Выбор формата
            if format_type == "xlsx":
                format_obj = base_formats.XLSX()
                file_data = format_obj.export_data(dataset)
                filename = "exported_orders.xlsx"
                content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:  # csv по умолчанию
                format_obj = base_formats.CSV()
                file_data = format_obj.export_data(dataset)
                filename = "exported_orders.csv"
                content_type = "text/csv"

            response = HttpResponse(file_data, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            logger.error(f"Ошибка при экспорте заказов: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Недопустимый метод"}, status=400)


@csrf_exempt
def delete_orders(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_ids = data.get("order_ids", [])

            if not order_ids:
                return JsonResponse({"success": False, "error": "Нет выбранных заказов"}, status=400)

            orders = OrderHistory.objects.filter(id__in=order_ids, shop=request.user.shop)
            count = orders.count()
            orders.delete()
            messages.success(request, f'Удалено заказов: {count}')
            
            return JsonResponse({"success": True, "deleted_count": count})
        except Exception as e:
            logger.error(f"Ошибка при удалении заказов: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Недопустимый метод"}, status=400)

@login_required
def total(request):
    shop = request.user.shop
    orders = OrderHistory.objects.filter(shop=shop).order_by('-created')
    filters = OrderHistoryFilter(request.GET, queryset=orders)
    orders_count = orders.count()
    number_per_page = request.user.shop.orderhistory_per_page

    # Получение даты начала и конца текущего месяца
    today = now().date()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Получение значений из запроса или установка значений по умолчанию
    date_gte = request.GET.get('created_min', first_day)
    date_lte = request.GET.get('created_max', last_day)

    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number, number_per_page)

    # Общий доход от продаж
    total_sales = SoldHistory.objects.filter(Q(created__gte=date_gte), Q(created__lte=date_lte), Q(shop=shop))\
        .annotate(total_per_sale=F('amount') * F('quantity'))\
        .aggregate(total_sales=Sum('total_per_sale'))['total_sales'] or 0

    # Общее количество проданных товаров
    total_sales_quantity = SoldHistory.objects.filter(Q(shop=shop) & Q(created__gte=date_gte) & Q(created__lte=date_lte))\
        .aggregate(total_sum=Sum('quantity'))['total_sum'] or 0

    # Средний чек
    try:
        average_receipt = round(total_sales / total_sales_quantity)
    except ZeroDivisionError:
        average_receipt = 0

    # Самый продаваемый товар
    top_product = SoldHistory.objects.filter(Q(created__gte=date_gte), Q(created__lte=date_lte), Q(shop=shop))\
        .values('product__name', 'product__id')\
        .annotate(total_quantity=Sum('quantity'))\
        .order_by('-total_quantity')\
        .first()

    top_selling_product = {
        "name": top_product['product__name'] if top_product else "Нет данных",
        "quantity": top_product['total_quantity'] if top_product else 0,
    }

    # Оплаты наличными
    cash_total = OrderHistory.objects.filter(shop=shop, created__gte=date_gte, created__lte=date_lte)\
        .aggregate(total_cash=Sum('cash_payment'))['total_cash'] or 0

    # Оплаты картой
    card_total = OrderHistory.objects.filter(shop=shop, created__gte=date_gte, created__lte=date_lte)\
        .aggregate(total_card=Sum('online_payment'))['total_card'] or 0

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'average_receipt': average_receipt,
        'top_selling_product': top_selling_product,
        'cash_payments': cash_total,
        'card_transfers': card_total,
        'filters': filters,
        'date_gte': date_gte,
        'date_lte': date_lte,
        'orders_count':orders_count,
        'number_per_page':number_per_page
    }
    return render(request, 'history/total.html', context)


@login_required
def sales(request):
    sales = SoldHistory.objects.filter(shop=request.user.shop).order_by('-created')
    number_per_page = request.user.shop.salehistory_per_page

    filters = SoldHistoryFilter(request.GET, queryset=sales)
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number, number_per_page)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters,
        'number_per_page':number_per_page
    }
    return render(request, 'history/sales.html', context)


@login_required
def incomes(request):
    incomes = IncomeHistory.objects.filter(shop=request.user.shop).order_by('-created')
    number_per_page = request.user.shop.incomehistory_per_page
    filters = IncomeHistoryFilter(request.GET, queryset=incomes)
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number, number_per_page)

    context = {
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters,
        'number_per_page':number_per_page
    }
    return render(request, 'history/incomes.html', context)


@login_required
def sales_delete(request, pk):
    sale = SoldHistory.objects.get(id=pk)
    sale.product.quantity += sale.quantity
    sale.product.save()
    LogHistory.objects.create(user=request.user, message='Удалена продажа', shop=request.user.shop, object=sale.product.name)
    sale.delete()

    return redirect('sold-history')


@login_required
def income_delete(request, pk):
    income = IncomeHistory.objects.get(id=pk)
    product = income.product
    product.quantity -= income.quantity
    product.save()
    LogHistory.objects.create(user=request.user, message='Удалена поставка', shop=request.user.shop, object=product.name)
    income.delete()
    return redirect('income-history')


@login_required
def order_delete(request, pk):
    # Получаем заказ по ID
    order = OrderHistory.objects.get(id=pk)

    for i in order.soldhistory_set.all():
        product = i.product
        product.quantity += i.quantity
        product.save()
    
    LogHistory.objects.create(user=request.user, message='Удалена очередь', shop=request.user.shop, object=f'{order.id} - {order.created}')
    order.delete()

    return redirect('total')


def log_list(request):
    logs = LogHistory.objects.filter(shop=request.user.shop).order_by('-created')
    filters = LogHistoryFilter(request.GET, queryset=logs)
    page_number = request.GET.get('page')
    page_obj, visible_pages = paginate(request, filters.qs, page_number)
    context = {
        'logs': logs,
        'page_obj': page_obj,
        'visible_pages': visible_pages,
        'filters': filters
    }
    return render(request, 'history/logs.html', context)

def receipt(request, pk):
    order = OrderHistory.objects.get(id=pk)
    return render(request, 'receipt.html', {'order': order})