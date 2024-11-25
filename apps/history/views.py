from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from .models import *
from django.contrib.auth.decorators import login_required

@login_required
def history(request):
    orders = OrderHistory.objects.filter(shop=request.user.shop).order_by('-created')

    context = {
        'orders': orders,
    }

    return render(request, 'history/history.html', context)


def sales(request):
    sales = SoldHistory.objects.filter(shop=request.user.shop).order_by('-created')
    context = {
        'sales': sales
    }
    return render(request, 'history/sales.html', context)


def incomes(request):
    incomes = IncomeHistory.objects.filter(shop=request.user.shop).order_by('-created')
    context = {
        'incomes': incomes
    }
    return render(request, 'history/incomes.html', context)


def sales_delete(request, pk):
    sale = SoldHistory.objects.get(id=pk)
    sale.product.quantity += sale.quantity
    sale.product.save()
    sale.delete()
    return redirect('sold-history')


def incomes_delete(request, pk):
    income = IncomeHistory.objects.get(id=pk)
    product = income.product
    product.quantity -= income.quantity
    product.save()
    income.delete()
    return redirect('income-history')

def order_delete(request, pk):
    order = OrderHistory.objects.get(id=pk)
    for i in order.soldhistory_set.all():
        product = i.product
        product.quantity += i.quantity
        product.save()
    order.delete()
    return redirect('history')

def income_delete(request, pk):
    income = Income.objects.get(id=pk)
    for i in income.incomehistory_set.all():
        product = i.product
        product.quantity -= i.quantity
        product.save()
    income.delete()
    return redirect('history')