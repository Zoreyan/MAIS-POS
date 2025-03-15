import csv
import logging
from celery import shared_task
from django.core.exceptions import ValidationError
from .models import Shop, Category, Product

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