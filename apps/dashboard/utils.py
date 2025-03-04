from .models import *
from apps.history.models import *
from django.db.models import Sum, F
from .forms import *
from django.db.models.functions import TruncMonth

from apps.product.models import Product
from apps.finance.models import Expense
from apps.history.models import *
from django.db.models import Sum, F

def get_totals(request, shop, selected_year, selected_month):
    total_products = Product.objects.filter(shop=shop).count()
    total_expenses = Expense.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).aggregate(total=Sum('amount'))['total'] or 0
    total_incomes = IncomeHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).aggregate(total=Sum('amount') * Sum('quantity'))['total'] or 0
    total_sales = SoldHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).annotate(
    total_per_sale=F('amount') * F('quantity')).aggregate(total_sales=Sum('total_per_sale'))['total_sales'] or 0
    product_profit = SoldHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).annotate(
    total_profit=F('quantity') * F('amount') - F('product__cost_price')).aggregate(total=Sum('total_profit'))['total'] or 0
    total_sales_quantity = SoldHistory.objects.filter(shop=shop, created__year=selected_year, created__month=selected_month).aggregate(total_sum=Sum('quantity'))['total_sum'] or 0
    return total_products, total_expenses, total_incomes, total_sales, product_profit, total_sales_quantity

def get_previous_totals(request, shop, selected_year, selected_month):
    previous_month = selected_month - 1 if selected_month > 1 else 12
    previous_year = selected_year if selected_month > 1 else selected_year - 1
    previous_expenses = Expense.objects.filter(shop=shop, created__year=previous_year, created__month=previous_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_incomes = IncomeHistory.objects.filter(shop=shop, created__year=previous_year, created__month=previous_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_sales = SoldHistory.objects.filter(shop=shop, created__year=previous_year, created__month=previous_month).annotate(
    total_per_sale=F('amount') * F('quantity')).aggregate(total=Sum('total_per_sale'))['total'] or 0
    previous_sales_quantity = SoldHistory.objects.filter(shop=shop, created__year=previous_year, created__month=previous_month).aggregate(total=Sum('quantity'))['total'] or 0
    return previous_expenses, previous_incomes, previous_sales, previous_sales_quantity

def get_growth_calculations(request, total_expenses, total_incomes, total_sales, previous_expenses, previous_incomes, previous_sales, total_sales_quantity, previous_sales_quantity):
    expenses_growth = calculate_growth(request, total_expenses, previous_expenses)
    incomes_growth = calculate_growth(request, total_incomes, previous_incomes)
    sales_growth = calculate_growth(request, total_sales, previous_sales)
    sales_quantity_growth = calculate_growth(request, total_sales_quantity, previous_sales_quantity)
    return expenses_growth, incomes_growth, sales_growth, sales_quantity_growth


# Вычисляем рост показателей
def calculate_growth(request, current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100

def get_sales_by_month(request):
    sales_by_month = SoldHistory.objects.annotate(
        month=TruncMonth('created')  # Группируем по месяцам
    ).values('month').annotate(
        total_sales=Sum('quantity')  # Суммируем продажи за каждый месяц
    ).order_by('month')

    return sales_by_month

