import csv
import io
import requests
from django.db import transaction
from django.core.files.base import ContentFile
from .models import Product, Shop, Category
from celery import shared_task

@shared_task(bind=True)
def import_products_from_csv(self, file_data, shop_id):
    try:
        f = io.StringIO(file_data)
        reader = csv.DictReader(f)
        rows = list(reader)
        total = len(rows)
        imported_count = 0

        shop = Shop.objects.get(id=shop_id)

        with transaction.atomic():
            for i, row in enumerate(rows, start=1):
                category_name = row['category']
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    shop=shop
                )
                product = Product(
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

                # Обработка изображения по ссылке
                image_url = row.get('image', None) 
                if image_url:
                    try:
                        img_response = requests.get(image_url)
                        img_response.raise_for_status()
                        product_image = ContentFile(img_response.content)
                        product.image.save(f"{product.name}.jpg", product_image, save=True)
                    except requests.exceptions.RequestException:
                        pass

                product.save()
                imported_count += 1

                # Обновляем прогресс
                self.update_state(state='PROGRESS', meta={'current': i, 'total': total})

        return f"Импорт завершен! Импортировано товаров: {imported_count}"
    except Exception as e:
        return f"Ошибка при импорте: {e}"
