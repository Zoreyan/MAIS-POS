from apps.history.models import *
from .models import *

def create_sale(request, cash_payment, online_payment, change, discount, products):
    if cash_payment > 0 and online_payment > 0:
        payment_method = 'split'  # Если оба поля заполнены, это split-оплата
    elif cash_payment > 0:
        payment_method = 'cash'  # Если только cash_payment > 0, это наличные
    elif online_payment > 0:
        payment_method = 'online'  # Если только online_payment > 0, это онлайн-оплата
    else:
        payment_method = 'online'
    order = OrderHistory.objects.create(
        user=request.user,
        shop=request.user.shop,
        cash_payment=cash_payment,
        online_payment=online_payment,
        change=change,
        discount=discount,
        payment_method=payment_method
    )
    for item in products:
        product = Product.objects.get(id=item['id'])
        quantity = int(item['quantity'])

        # Сохраняем текущую цену продукта
        SoldHistory.objects.create(
            shop=request.user.shop,
            order=order,
            product=product,
            quantity=quantity,
            amount=product.discounted_price(),
        )
        product.quantity -= quantity
        product.save()