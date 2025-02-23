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
import csv
import io
import requests
from django.db import transaction, IntegrityError
from django.core.files.base import ContentFile
from .models import Product, Shop, Category
from celery import shared_task
from pydantic import BaseModel, ValidationError, confloat, constr
from typing import Optional

class ProductModel(BaseModel):
    name: constr(min_length=1)
    category: constr(min_length=1)
    price: confloat(gt=0)
    sale_price: Optional[float] = None
    discount: Optional[float] = None
    quantity: Optional[float] = None
    min_quantity: Optional[float] = None
    unit: Optional[str] = 'шт'  # Используем явное значение по умолчанию

def validate_csv(row):
    try:
        product = ProductModel(**row)
        return None
    except ValidationError as e:
        return e.errors()


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


@shared_task(bind=True)
def import_products_from_csv(self, file_data, shop_id):
    errors = []
    imported_count = 0
    try:
        f = io.StringIO(file_data)
        reader = csv.DictReader(f)
        rows = list(reader)
        total = len(rows)
        shop = Shop.objects.get(id=shop_id)

        with transaction.atomic():
            for i, row in enumerate(rows, start=1):
                try:
                    validation_errors = validate_csv(row)
                    if validation_errors:
                        for err in validation_errors:
                            errors.append(f"Ошибка в строке {i}: {err['msg']}")

                        continue  

                    # Дополнительные проверки
                    if len(row.get('unit', 'шт')) > 2:
                        errors.append(f"Ошибка в строке {i}: Поле 'unit' (единица измерения) не может содержать более 2 символов. Проверьте значение.")
                        continue
                    
                    category, _ = Category.objects.get_or_create(name=row['category'], shop=shop)

                    product, created = Product.objects.get_or_create(
                        name=row['name'],
                        description=row.get('description', ''),
                        shop=shop,
                        category=category,
                        price=row['price'],
                        sale_price=row.get('sale_price', 0),
                        discount=row.get('discount', 0),
                        unit=row.get('unit', 'шт'),
                        bar_code=row.get('bar_code', None),
                        quantity=row.get('quantity', 0),
                        min_quantity=row.get('min_quantity', 0)
                    )

                    # Обработка изображений
                    image_url = row.get('image', None)
                    if image_url:
                        try:
                            img_response = requests.get(image_url)
                            img_response.raise_for_status()
                            product_image = ContentFile(img_response.content)
                            product.image.save(f"{product.name}.jpg", product_image, save=True)
                        except requests.exceptions.RequestException:
                            errors.append(f"Ошибка загрузки изображения для товара '{row['name']}'. Проверьте корректность URL изображения.")

                    if created:
                        imported_count += 1

                    self.update_state(state='PROGRESS', meta={'current': i, 'total': total})

                except IntegrityError as ie:
                    # Обработка ошибок базы данных
                    if 'product_product_bar_code_key' in str(ie):
                        errors.append(f"Ошибка при импорте товара '{row.get('name')}'. Товар с таким баркодом '{row.get('bar_code')}' уже существует в базе данных.")
                    elif 'value too long for type character varying(2)' in str(ie):
                        errors.append(f"Ошибка при импорте товара '{row.get('name')}'. Значение в одном из полей слишком длинное (максимум 2 символа). Проверьте значение.")
                    else:
                        errors.append(f"Ошибка при сохранении товара '{row.get('name')}'. Не удалось обработать данные: {str(ie)}")
                except ValueError as ve:
                    errors.append(f"Ошибка валидации для товара '{row.get('name')}'. Некорректный формат данных: {ve}")
                except KeyError as ke:
                    errors.append(f"Ошибка в строке {i}: Не найден обязательный параметр '{ke.args[0]}'. Проверьте структуру данных.")
                except Exception as e:
                    errors.append(f"Общая ошибка при импорте товара '{row.get('name')}'. Неизвестная ошибка: {str(e)}")

        if errors:
            return {'status': 'PARTIAL_SUCCESS', 'imported': imported_count, 'errors': errors}
        else:
            return {'status': 'SUCCESS', 'imported': imported_count}

    except Exception as e:
        return {'status': 'FAILURE', 'errors': [f"Неизвестная ошибка: {str(e)}"]}
