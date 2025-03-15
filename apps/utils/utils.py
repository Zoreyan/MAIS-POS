import random
import string
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator
from apps.history.models import *
from apps.product.models import *

def generate_text():
    digits = ''.join(random.choice(string.digits) for _ in range(4))
    return f'{digits}'


def check_permission(func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'cashier':
            return redirect('total')
        else:
            return func(request, *args, **kwargs)
    return wrapper


def delete_obj(request, obj, pk, message):
    object = get_object_or_404(obj, id=pk)
    LogHistory.objects.create(user=request.user, shop=request.user.shop, message=message, object=object.id)
    object.delete()


def paginate(request, products, page_number, per_page=20):
    paginator = Paginator(products.order_by('-id'), per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    current_page = page_obj.number
    total_pages = paginator.num_pages
    delta = 3

    start_page = max(current_page - delta, 1)
    end_page = min(current_page + delta, total_pages)
    visible_pages = range(start_page, end_page + 1)
    return page_obj, visible_pages



