from django.shortcuts import render
from apps.product.models import Product, Shop

def index(request):
    context = {
    }
    return render(request, 'client/index.html', context)