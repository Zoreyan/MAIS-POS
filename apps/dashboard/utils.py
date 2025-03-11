from apps.product.models import Product
from apps.finance.models import Expense
from apps.history.models import SoldHistory, IncomeHistory
from django.db.models.functions import TruncMonth
from django.db.models import Sum, F
from django.utils import timezone


def get_aggregated_sum(model, shop, date_filter, field, default=0):
    return model.objects.filter(shop=shop, **date_filter).aggregate(total=Sum(field))['total'] or default

def get_today(request):
    shop = request.user.shop
    today = timezone.now()
    date_filter = {'created__year': today.year, 'created__month': today.month, 'created__day': today.day}

    return {
        'today_expenses': get_aggregated_sum(Expense, shop, date_filter, 'amount'),
        'today_sales_quantity': get_aggregated_sum(SoldHistory, shop, date_filter, 'quantity'),
        'product_profit': get_aggregated_sum(SoldHistory, shop, date_filter, (F('amount') - F('product__cost_price')) * F('quantity')),
        'today_sales': get_aggregated_sum(SoldHistory, shop, date_filter, F('amount') * F('quantity')),
        'today_incomes': get_aggregated_sum(IncomeHistory, shop, date_filter, 'amount', default=0)
    }


def get_totals(shop, year, month):
    date_filter = {'created__year': year, 'created__month': month}
    return {
        'total_products': Product.objects.filter(shop=shop).count(),
        'total_expenses': get_aggregated_sum(Expense, shop, date_filter, 'amount'),
        'total_incomes': get_aggregated_sum(IncomeHistory, shop, date_filter, 'amount'),
        'total_sales': get_aggregated_sum(SoldHistory, shop, date_filter, F('amount') * F('quantity')),
        'profit': get_aggregated_sum(SoldHistory, shop, date_filter, (F('amount') - F('product__cost_price')) * F('quantity')),
        'sales_quantity': get_aggregated_sum(SoldHistory, shop, date_filter, 'quantity'),
    }


def get_previous_totals(shop, year, month):
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    date_filter = {'created__year': prev_year, 'created__month': prev_month}
    return {
        'previous_expenses': get_aggregated_sum(Expense, shop, date_filter, 'amount'),
        'previous_incomes': get_aggregated_sum(IncomeHistory, shop, date_filter, 'amount'),
        'previous_sales': get_aggregated_sum(SoldHistory, shop, date_filter, F('amount') * F('quantity')),
        'previous_sales_quantity': get_aggregated_sum(SoldHistory, shop, date_filter, 'quantity'),
    }


def get_growth_calculations(total_expenses, total_incomes, total_sales, previous_expenses, previous_incomes, previous_sales, total_sales_quantity, previous_sales_quantity):
    expenses_growth = calculate_growth(total_expenses, previous_expenses)
    incomes_growth = calculate_growth(total_incomes, previous_incomes)
    sales_growth = calculate_growth(total_sales, previous_sales)
    sales_quantity_growth = calculate_growth(total_sales_quantity, previous_sales_quantity)
    return {
        'expenses_growth': expenses_growth,
        'incomes_growth': incomes_growth,
        'sales_growth': sales_growth,
        'sales_quantity_growth': sales_quantity_growth
    }


# Вычисляем рост показателей
def calculate_growth(current, previous):
    if not previous:
        return 100 if current else 0
    return (current - previous) / previous * 100


def get_sales_by_month(queryset, **kwargs):
    return queryset.objects.filter(**kwargs).annotate(
        month=TruncMonth('created')
    ).values('month').annotate(
        total_sales=Sum('quantity')
    ).order_by('month')