from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.db.models import Sum
from .models import Expense
from apps.history.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_POST
import json


@login_required
def get_chart_data(request):
    # Получаем данные по продажам, прибыли и расходам, агрегированные по месяцам
    sales_data = OrderHistory.objects.values('created__month').annotate(
        total_sales=Sum('amount'),    # Сумма стоимости продаж
        total_profit=Sum('profit'),   # Сумма прибыли
    ).order_by('created__month')
    
    expend_data = Expense.objects.values('created__month').filter(shop=request.user.shop, status='paid').annotate(
        total_expend=Sum('amount')  # Сумма расходов
    ).order_by('created__month')
        
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    
    sales = [0] * 12
    profit = [0] * 12
    expenses = [0] * 12
    
    
    for sale in sales_data:
        month_index = sale['created__month'] - 1
        sales[month_index] = sale['total_sales']    # Сумма стоимости продаж
        profit[month_index] = sale['total_profit']  # Сумма прибыли
    
    for expend in expend_data:
        month_index = expend['created__month'] - 1
        expenses[month_index] = expend['total_expend']
        
    return JsonResponse({
        'months': months,
        'sales': sales,     # Стоимость продаж
        'profit': profit,   # Прибыль
        'expenses': expenses  # Расходы
    })


def extends_chart_data(request):
    expend_data = Expense.objects.annotate(month=TruncMonth('created')) \
                            .values('month', 'expend_type') \
                            .annotate(total_amount=Sum('amount')) \
                            .order_by('month')

    # Подготовка данных для графика
    months = []
    rent_data = []
    utilities_data = []
    salaries_data = []
    supplies_data = []
    other_data = []

    for data in expend_data:
        # Выводим для отладки
        print(f"Month: {data['month']}, Expense Type: {data['expend_type']}, Total Amount: {data['total_amount']}")
        
        month_name = data['month'].strftime('%B')  # Например, "January"
        if month_name not in months:
            months.append(month_name)

        # Сортируем по типам расходов
        if data['expend_type'] == 'rent':
            rent_data.append(data['total_amount'])
        elif data['expend_type'] == 'utilities':
            utilities_data.append(data['total_amount'])
        elif data['expend_type'] == 'salaries':
            salaries_data.append(data['total_amount'])
        elif data['expend_type'] == 'supplies':
            supplies_data.append(data['total_amount'])
        elif data['expend_type'] == 'other':
            other_data.append(data['total_amount'])

    # Если для типа расхода нет данных в каком-то месяце, заполняем 0
    max_month = len(months)
    for data_list in [rent_data, utilities_data, salaries_data, supplies_data, other_data]:
        # Дополняем список до 12 месяцев (0 для отсутствующих данных)
        data_list += [0] * (12 - max_month)

    # Список месяцев на русском языке
    months_list = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

    # Возвращаем данные в формате JSON
    return JsonResponse({
        'months': months_list[:max_month],  # Передаем только те месяцы, которые есть в данных
        'rent_data': rent_data,
        'utilities_data': utilities_data,
        'salaries_data': salaries_data,
        'supplies_data': supplies_data,
        'other_data': other_data,
    })

def finance_list(request):
    return render(request, 'finance/list.html')

def create(request):
    # Получаем expend_type из GET-запроса
    expend_type = request.GET.get('type')
    expend_display_name = dict(Expense.EXPEND_TYPE_CHOICES).get(expend_type)
    
    # Инициализируем форму с начальным значением expend_type
    form = ExpenseForm(initial={'expend_type': expend_type})
    
    if request.method == 'POST':
        # При POST-запросе создаем форму с данными из запроса
        form = ExpenseForm(request.POST)
        
        # Проверяем валидность формы
        if form.is_valid():
            # Устанавливаем значение expend_type перед сохранением объекта
            expend = form.save(commit=False)
            expend.expend_type = expend_type
            expend.shop = request.user.shop
            if expend_type == 'other':
                expend.description = form.cleaned_data['description']
            else:
                expend.description = expend_display_name

            if expend.status == 'paid':
             # Предположим, что для конкретного shop есть только один объект order
                order = OrderHistory.objects.filter(shop=request.user.shop).first()
                if order:  # Проверяем, что order существует
                    order.profit = Decimal(order.profit) - Decimal(expend.amount)
                    order.save()  # Сохраняем изменения

            expend.save()
            return redirect('expends')
        else:
            print(form.errors, expend_type)
    
    context = {
        'form': form,
        'expend_type': expend_type,
        'expend_display_name': expend_display_name
    }
    return render(request, 'finance/create.html', context)

def expends(request):
    expends = Expense.objects.exclude(expend_type='salaries').filter(shop=request.user.shop).order_by('-id')

    context = {
        'expends': expends
    }
    return render(request, 'finance/expends.html', context)

def expend_update(request, pk):
    # Находим объект Expense по первичному ключу (pk)
    expend = get_object_or_404(Expense, id=pk)
    start_day = expend.start_date
    end_day = expend.end_date
    
    # Получаем тип расхода (expend_type) из объекта и название для отображения
    expend_type = expend.expend_type
    expend_display_name = dict(Expense.EXPEND_TYPE_CHOICES).get(expend_type)
    
    # Инициализируем форму с данными объекта
    form = ExpenseForm(instance=expend, initial={'expend_type': expend_type})

    if request.method == 'POST':
        # При POST-запросе обновляем форму с данными из запроса
        form = ExpenseForm(request.POST, instance=expend)
        
        if form.is_valid():
            # Сохраняем значения start_date и end_date, если они не были изменены
            expend.start_date = form.cleaned_data.get('start_date', start_day)
            expend.end_date = form.cleaned_data.get('end_date', end_day)
            expend = form.save(commit=False)
            expend.expend_type = expend_type
            expend.shop = request.user.shop
            # Устанавливаем описание в зависимости от типа расхода
            if expend_type == 'other':
                expend.description = form.cleaned_data['description']
            else:
                expend.description = expend_display_name

            if expend.status == 'paid':
            # Предположим, что для конкретного shop есть только один объект order
                order = OrderHistory.objects.filter(shop=request.user.shop).first()  # Используем first() для получения первого объекта или None, если его нет
    
                if order:
                    order.profit = Decimal(order.profit) - Decimal(expend.amount)
                    order.save()

            expend.save()
            return redirect('expends')
        else:
            print(form.errors, expend_type)
    
    context = {
        'form': form,
        'expend_type': expend_type,
        'expend_display_name': expend_display_name
    }
    return render(request, 'finance/update.html', context)


def expend_delete(request, pk):
    # Настрой объект Expense по первичному ключу (pk)
    expend = get_object_or_404(Expense, id=pk)
    expend.delete()
    return redirect('expends')

def salary_list(request):
    salaries = Expense.objects.filter(expend_type='salaries', shop=request.user.shop)
    return render(request, 'finance/salaries.html', {'salaries': salaries})