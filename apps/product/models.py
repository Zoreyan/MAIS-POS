from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, verbose_name='Магазин', null=True)
    name = models.CharField(max_length=100, verbose_name='Название')


    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


# comment
class Shop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100, 
        verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'


    def __str__(self):
        return self.name

# Create your models here.
class Product(models.Model):
    UNITS = [
        ('шт', 'шт'),
        ('кг', 'кг'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Название')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Базовая цена', null=True)
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Продажная цена',
        default=0
    )
    discount = models.IntegerField(default=0, verbose_name='Скидка', null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    unit = models.CharField(max_length=2, choices=UNITS, default='шт', verbose_name='Единица измерения', null=True)
    bar_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='Штрихкод')
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    is_favorite = models.BooleanField(default=False, verbose_name='Избранный')
    min_quantity = models.IntegerField(default=10, verbose_name='Минимальный остаток')


    class Meta:
        unique_together = ('bar_code', 'shop')
        ordering = ['name']
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
    
    def discounted_price(self):
        if self.discount > 0:
            discount_multiplier = Decimal(1) - (Decimal(self.discount) / Decimal(100))
            return round(self.sale_price * discount_multiplier, 1)
        return round(self.sale_price, 1)

    def __str__(self):
        return self.name

    def in_stock(self):
        return self.quantity > 0
    
