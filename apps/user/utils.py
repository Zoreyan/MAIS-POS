import random
import string
from django.shortcuts import redirect

def generate_text():
    symbols = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
    digits = ''.join(random.choice(string.digits) for _ in range(3))
    return f'{symbols}-{digits}'


def check_permission(func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'cashier':
            return redirect('total')
        else:
            return func(request, *args, **kwargs)
    return wrapper