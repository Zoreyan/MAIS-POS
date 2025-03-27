import csv
import logging
from celery import shared_task
from django.core.exceptions import ValidationError
from .models import Shop, Category, Product
from apps.user.models import User
from apps.user.models import Notification
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def import_products_from_csv(self, file_data, shop_id):
    import_quantity = 0
    try:
        reader = csv.DictReader(file_data.splitlines())
        rows = list(reader)
        total = len(rows)
        shop = Shop.objects.get(id=shop_id)

        for i, row in enumerate(rows, start=1):
            try:
                # Проверка обязательных полей
                required_fields = ['name', 'category']
                for field in required_fields:
                    if field not in row:
                        logger.error(f"Отсутствует обязательное поле: {field}")
                        continue

                # Создание или получение категории
                category, _ = Category.objects.get_or_create(name=row['category'], shop=shop)

                # Создание или обновление товара
                product, created = Product.objects.get_or_create(
                    name=row['name'],
                    shop=shop,
                    category=category,
                    cost_price=row.get('cost_price', 0),
                    sale_price=row.get('sale_price', 0),
                    discount=row.get('discount', 0),
                    unit=row.get('unit', 'шт'),
                    bar_code=row.get('bar_code', None),
                    quantity=row.get('quantity', 0),
                    min_quantity=row.get('min_quantity', 10)
                )

                if created:
                    import_quantity += 1

                # Обновление прогресса
                self.update_state(state='PROGRESS', meta={'current': i, 'total': total})
            except Exception as ex:
                logger.error(f"Ошибка при обработке строки {i}: {ex}")

        # Успешное завершение задачи
        self.update_state(state='SUCCESS', meta={'imported': import_quantity})
        return {'status': 'SUCCESS', 'imported': import_quantity}

    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        return {'status': 'FAILURE', 'errors': [f"Неизвестная ошибка: {str(e)}"]}

@shared_task
def check_product_stock(product_ids, shop_id):

    if not product_ids:
        return "No products provided."

    low_stock_products = []

    try:
        shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
        return f"Shop with id {shop_id} does not exist."

    users = User.objects.filter(shop=shop)

    for product_id in product_ids:
        if not product_id:
            continue

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        if product.quantity < product.min_quantity:
            low_stock_products.append({
                'name': product.name,
                'quantity': product.quantity,
                'min_quantity': product.min_quantity
            })

    if low_stock_products:
        if shop.system_notifications:
            notification_title = f"Низкий запас на {len(low_stock_products)} товар(ов)"
            notification_details = render_to_string(
                'user/notification_details_table.html',
                {'products': low_stock_products}
            )
            notification = Notification.objects.create(
                shop=shop,
                category="Низкий запас",
                title=notification_title,
                details=notification_details
            )
            notification.is_not_read.set(users)

    return f"Checked products. Low stock found for {len(low_stock_products)} products."