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
from apps.finance.models import Expense
from datetime import datetime
from apps.history.models import *
from datetime import datetime, timedelta
from django.db.models import Sum, F
from django.utils.timezone import make_aware, is_aware, now
import calendar
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from django.utils.dateformat import DateFormat




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

def calculate_growth(current, previous):
    """
    Функция для вычисления роста.
    """
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

@login_required
def dashboard(request):
    # Получаем start_month и end_month из GET-параметров
    start_month = request.GET.get('start_month', None)
    end_month = request.GET.get('end_month', None)
    current_year = datetime.now().year
    start_year = int(start_month.split('-')[0]) if start_month else current_year
    end_year = int(end_month.split('-')[0]) if end_month else current_year
    
    MONTHS_RU = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]

    shop = request.user.shop
      
    # Значения по умолчанию - текущий месяц
    if not start_month and not end_month:
        today = datetime.now()
        start_month = today.strftime('%Y-%m')

    expenses = None
    total_incomes_current = 0
    total_expenses_current = 0
    total_profit_current = 0
    selected_period_display = ""
    income_growth = 0
    expense_growth = 0
    profit_growth = 0

    def parse_month(month_str):
        """Парсинг строки в datetime и обработка ошибок."""
        try:
            return datetime.strptime(month_str + '-01', '%Y-%m-%d')
        except ValueError:
            return None

    # Если заданы оба start_month и end_month, фильтруем по диапазону
    if start_month and end_month:
        start_date = parse_month(start_month)
        end_date = parse_month(end_month)

        if start_date and end_date:
            _, last_day = calendar.monthrange(end_date.year, end_date.month)
            end_date = end_date.replace(day=last_day)

            start_date = make_aware(start_date)
            end_date = make_aware(end_date)

            expenses = Expense.objects.filter(created__range=(start_date, end_date), shop=shop)
            total_incomes_current = OrderHistory.objects.filter(order_type='sale', created__range=(start_date, end_date), shop=shop).aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses_current = Expense.objects.filter(created__range=(start_date, end_date), shop=shop).aggregate(Sum('amount'))['amount__sum'] or 0
            total_profit_current = OrderHistory.objects.filter(order_type='sale', created__range=(start_date, end_date), shop=shop).aggregate(Sum('profit'))['profit__sum'] or 0
            selected_period_display = f"с {MONTHS_RU[int(start_month.split('-')[1]) - 1]} {start_month[:4]} до {MONTHS_RU[int(end_month.split('-')[1]) - 1]} {end_month[:4]}"

    # Если выбран только start_month, фильтруем только этот месяц
    elif start_month:

        start_date = parse_month(start_month)

        if start_date:

            _, last_day = calendar.monthrange(start_date.year, start_date.month)
            end_date = start_date.replace(day=last_day)

            start_date = make_aware(start_date)
            end_date = make_aware(end_date)

            expenses = Expense.objects.filter(created__range=(start_date, end_date), shop=shop)
            total_incomes_current = OrderHistory.objects.filter(order_type='sale', created__range=(start_date, end_date), shop=shop).aggregate(Sum('amount'))['amount__sum'] or 0
            total_expenses_current = Expense.objects.filter(created__range=(start_date, end_date), shop=shop).aggregate(Sum('amount'))['amount__sum'] or 0
            total_profit_current = OrderHistory.objects.filter(order_type='sale', created__range=(start_date, end_date), shop=shop).aggregate(Sum('profit'))['profit__sum'] or 0
            selected_period_display = f"за {MONTHS_RU[int(start_month.split('-')[1]) - 1]} {start_month[:4]}"

            # Вычисление роста на основе прошлого месяца
            previous_month = start_date - relativedelta(months=1)
            previous_start_date = previous_month.replace(day=1)
            _, previous_last_day = calendar.monthrange(previous_month.year, previous_month.month)
            previous_end_date = previous_month.replace(day=previous_last_day)

            previous_start_date = previous_start_date.replace(tzinfo=None)
            previous_end_date = previous_end_date.replace(tzinfo=None)

            previous_incomes = OrderHistory.objects.filter(
                order_type='sale',
                created__range=(make_aware(previous_start_date), make_aware(previous_end_date)),
                shop=shop
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            previous_expenses = Expense.objects.filter(
                created__range=(make_aware(previous_start_date), make_aware(previous_end_date)),
                shop=shop
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            previous_profit = OrderHistory.objects.filter(
                order_type='sale',
                created__range=(make_aware(previous_start_date), make_aware(previous_end_date)),
                shop=shop
            ).aggregate(Sum('profit'))['profit__sum'] or 0

            income_growth = calculate_growth(total_incomes_current, previous_incomes)
            expense_growth = calculate_growth(total_expenses_current, previous_expenses)
            profit_growth = calculate_growth(total_profit_current, previous_profit)
    elif end_month:
        first_order = OrderHistory.objects.filter(shop=shop).order_by('created').first()
        first_expense = Expense.objects.filter(shop=shop).order_by('created').first()
        
        end_date = datetime.strptime(end_month + '-01', '%Y-%m-%d')
        _, last_day = calendar.monthrange(end_date.year, end_date.month)
        end_date = datetime.strptime(end_month + f'-{last_day}', '%Y-%m-%d')

        first_date = None
        if first_order and first_expense:
            first_date = min(first_order.created, first_expense.created)
        elif first_order:
            first_date = first_order.created
        elif first_expense:
            first_date = first_expense.created

        if first_date:
            start_date = first_date.replace(day=1)
        else:
            start_date = datetime(2024, 1, 1)

        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)

        if end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)

        start_date = make_aware(start_date)
        end_date = make_aware(end_date)

        expenses = Expense.objects.filter(created__range=(start_date, end_date), shop=shop)
        total_incomes_current = OrderHistory.objects.filter(order_type='sale', created__range=(start_date, end_date), shop=shop).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses_current = Expense.objects.filter(created__range=(start_date, end_date), shop=shop).aggregate(Sum('amount'))['amount__sum'] or 0
        total_profit_current = OrderHistory.objects.filter(order_type='sale', created__range=(start_date, end_date), shop=shop).aggregate(Sum('profit'))['profit__sum'] or 0
        selected_period_display = f"до {MONTHS_RU[int(end_month.split('-')[1]) - 1]} {end_month[:4]}"

    # Получаем самые продаваемые товары
    sold_products = Product.objects.filter(shop=shop).annotate(total_quantity=Sum('soldhistory__quantity'), total_sum=Sum('soldhistory__quantity') * F('sale_price')).order_by('-total_quantity')[:5]
    
    expense_types = {
        "rent": Decimal(0),
        "utilities": Decimal(0),
        "salaries": Decimal(0),
        "supplies": Decimal(0),
        "other": Decimal(0),
    }
    # Проходим по расходам и суммируем по типам
    for expense in expenses:
        if expense.expend_type in expense_types:
            expense_types[expense.expend_type] += expense.amount

    total_expenses = sum(expense_types.values())
    expense_percentages = {
    key: (value / total_expenses * 100).quantize(Decimal('0.01')) if total_expenses > 0 else Decimal(0)
    for key, value in expense_types.items()
    }
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Преобразование Decimal в float
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    if start_month:
        start_year = int(start_month.split('-')[0])
        start_date = datetime(start_year, 1, 1)
    else:
        start_year = current_year
        start_date = datetime(current_year, 1, 1)

    if end_month:
        end_year = int(end_month.split('-')[0])
        _, last_day = calendar.monthrange(int(end_month.split('-')[0]), int(end_month.split('-')[1]))
        end_date = datetime(end_year, int(end_month.split('-')[1]), last_day)
    else:
        end_year = current_year
        end_date = datetime(current_year, 12, 31)

    if (end_date - start_date).days < 365:
        end_date = start_date + relativedelta(years=1) - timedelta(days=1)

    if end_month and not start_month:
        first_order = OrderHistory.objects.filter(shop=shop).order_by('created').first()
        first_expense = Expense.objects.filter(shop=shop).order_by('created').first()

        first_date = None
        if first_order and first_expense:
            first_date = min(first_order.created, first_expense.created)
        elif first_order:
            first_date = first_order.created
        elif first_expense:
            first_date = first_expense.created

        if first_date:
            start_date = first_date.replace(day=1)
        else:
            start_date = datetime(2024, 1, 1)

    if not is_aware(start_date):
        start_date = make_aware(start_date)

    if not is_aware(end_date):
        end_date = make_aware(end_date)

    months = []
    current_date = start_date
    while current_date <= end_date:
        months.append(current_date)
        current_date = current_date + relativedelta(months=1)

    # Сбор данных для графика
    income = []
    expenses = []
    profit = []

    for month in months:
        _, last_day = calendar.monthrange(month.year, month.month)
    
        if not is_aware(month):
            month = make_aware(month)

        month_end = month.replace(day=last_day)
        if not is_aware(month_end):
            month_end = make_aware(month_end)

        # Запросы для получения данных
        total_income = OrderHistory.objects.filter(
            order_type='sale', 
            created__range=(month, month_end), 
            shop=shop
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_expense = Expense.objects.filter(
            created__range=(month, month_end), 
            shop=shop
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_profit = OrderHistory.objects.filter(
            order_type='sale', 
            created__range=(month, month_end), 
            shop=shop
        ).aggregate(Sum('profit'))['profit__sum'] or 0

        income.append(float(total_income))
        expenses.append(float(total_expense))
        profit.append(float(total_profit))         

    chart_data = {
        'months': [m.strftime("%b %Y") for m in months],
        'income': income,
        'expenses': expenses,
        'profit': profit,
    }

    context = {
        'total_incomes_current': total_incomes_current,
        'total_expenses_current': total_expenses_current,
        'total_profit_current': total_profit_current,
        'income_growth': income_growth,
        'expense_growth': expense_growth,
        'profit_growth': profit_growth,
        'selected_period_display': selected_period_display,
        'sold_products': sold_products,

        'start_month': start_month,
        'end_month': end_month,

        'expense_types': json.dumps(expense_types, default=decimal_default),
        'expense_percentages': json.dumps(expense_percentages, default=decimal_default), 

        'chart_data_json': json.dumps(chart_data)
    }

    return render(request, 'dashboard.html', context)



@login_required
def settings_page(request, pk):
    shop = get_object_or_404(Shop, id=pk)
    form = ShopForm(instance=shop)
    
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)

        if form.is_valid():
            form.save()
            return redirect('settings_page', shop_id=shop.id)
    else:
        form = ShopForm(instance=shop)
    
    # Получаем объект магазина
    coordinates = shop.coordinates if shop else None

    # Проверяем наличие координат
    if coordinates:
        try:
            lat, lon = map(float, coordinates.split(','))  # Разбиваем и конвертируем координаты
            map_center = [lat, lon]  # Устанавливаем центр карты на координаты магазина
        except ValueError:
            map_center = [40.516018, 72.803835]  # Центр по умолчанию
    else:
        map_center = [40.516018, 72.803835]  # Центр по умолчанию

    # Создаём карту с центром на координаты магазина или по умолчанию
    m = Map(location=map_center, zoom_start=8)

    # Если у магазина есть координаты, добавляем маркер
    if coordinates:
        Marker(location=[lat, lon]).add_to(m)

    # Генерация HTML-кода карты
    map_html = m._repr_html_()

    context = {
        'form': form,
        'map_html': map_html,
        'shop': shop,
    }
    return render(request, 'settings_page.html', context)