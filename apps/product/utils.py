from apps.history.models import *
from .models import *
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site
from .tasks import check_product_stock

def generate_qr_code(order_id, request):
    """Генерирует QR-код для заказа с учётом текущего хоста"""
    current_site = get_current_site(request)
    qr_data = f"https://{current_site.domain}/history/receipt/{order_id}"

    qr = qrcode.make(qr_data)

    # Сохраняем QR-код в памяти
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)

    # Создаём файл для Django
    return ContentFile(qr_io.read(), name=f'qr_codes/order_{order_id}.png')

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

    qr_code_file = generate_qr_code(order.id, request)
    order.qr_code.save(f'order_{order.id}.png', qr_code_file, save=True)

    product_ids = []

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
        product_ids.append(product.id)

    check_product_stock.delay(product_ids, request.user.shop.id)
    
    return order