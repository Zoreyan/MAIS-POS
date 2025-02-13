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
    unit: Optional[str] = 'шт' or 'кг'

def validate_csv(row):
    try:
        product = ProductModel(**row)
        return None
    except ValidationError as e:
        return e.errors()

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
                            if err['type'] == 'string_too_short':
                                errors.append(f"Ошибка в строке {i}: Поле '{err['loc'][0]}' должно содержать хотя бы 1 символ. Проверьте значение.")
                            elif err['type'] == 'float_parsing':
                                errors.append(f"Ошибка в строке {i}: Поле '{err['loc'][0]}' должно содержать корректное числовое значение. Пример: 10.99.")
                            elif 'value too long for type character varying(2)' in err['msg']:
                                errors.append(f"Ошибка в строке {i}: Значение в поле '{err['loc'][0]}' слишком длинное. Оно должно быть не более 2 символов. Проверьте значение.")
                            else:
                                errors.append(f"Ошибка в строке {i}: {err['msg']}")

                        continue

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
