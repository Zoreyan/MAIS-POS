from celery import shared_task
from django.utils import timezone
from .models import Shop
from datetime import timedelta
from apps.dashboard.models import Notification
from apps.user.models import User
from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import Product
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)

@shared_task
def check_product_stock(products, shop_id):
    """
    Задача для проверки продуктов на наличие минимального количества.
    Если количество меньше минимального, создаём одно уведомление с таблицей товаров.
    """
    if not products:  # Проверяем, что список продуктов не пуст
        return "No products provided."

    # Список продуктов с низким запасом
    low_stock_products = []

    try:
        # Получаем магазин
        shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
        return f"Shop with id {shop_id} does not exist."

    # Получаем пользователей, связанных с магазином
    users = User.objects.filter(shop=shop)

    # Обрабатываем каждый продукт
    for product_data in products:
        product_id = product_data.get('id')
        if not product_id:
            continue  # Пропускаем, если id продукта отсутствует

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue  # Пропускаем, если продукт не найден

        if product.quantity < product.min_quantity:
            low_stock_products.append({
                'name': product.name,
                'quantity': product.quantity,
                'min_quantity': product.min_quantity
            })

    # Если есть продукты с низким запасом, создаём уведомление
    if low_stock_products:
        if shop.system_notifications:
            notification_title = f"Низкий запас на {len(low_stock_products)} товар(ов)"
            notification_details = render_to_string(
                'user/notification_details_table.html',
                {'products': low_stock_products}
            )
            notification = Notification.objects.create(
                shop=shop,
                category="Товар",
                title=notification_title,
                details=notification_details
            )
            notification.is_not_read.set(users)

        # Отправка email-уведомлений, если включены
        if shop.email_notifications:
            for user in users:
                if user.get_email_notification:
                    try:
                        send_mail(
                            subject="Магазин - Низкий запас товаров",
                            message="Некоторые товары имеют низкий запас. Проверьте уведомления.",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки почты пользователю {user.email}: {e}")

    return f"Checked products. Low stock found for {len(low_stock_products)} products."