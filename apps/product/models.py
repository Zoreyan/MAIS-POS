from django.db import models
from datetime import datetime
from mptt.models import MPTTModel, TreeForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal



class Category(MPTTModel):
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE, verbose_name='Магазин', null=True)
    name = models.CharField(max_length=100, verbose_name='Название')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='Родительская категория')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


# comment
class Shop(models.Model):
    image = models.ImageField(
        null=True, 
        blank=True, 
        upload_to='shops', 
        verbose_name='Изображение',
        default='shops/default_products.png'
    )
    name = models.CharField(
        max_length=100, 
        verbose_name='Название'
    )
    address = models.CharField(
        max_length=255, 
        verbose_name='Адрес'
    )
    coordinates = models.CharField(
        max_length=100, 
        verbose_name='Координаты', 
        null=True, 
        blank=True
    )
    contacts = models.TextField(
        verbose_name='Контакты', 
        null=True, 
        blank=True
    )
    about = models.TextField(
        verbose_name='О нас', 
        null=True, 
        blank=True
    )
    opening_hours = models.CharField(
        max_length=255, 
        verbose_name='Часы работы', 
        null=True, 
        blank=True
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Баланс")
    tariff = models.ForeignKey('dashboard.Tariff', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Текущий тариф")
    payment_due_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата следующей оплаты")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    auto_pay = models.BooleanField(default=True, verbose_name="Автоматическая оплата")
    email_notifications = models.BooleanField(default=True, verbose_name="Email уведомления")
    system_notifications = models.BooleanField(default=True, verbose_name="Системные уведомления")

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

        permissions = [
            ("can_manage_shop", "Can manage shop settings"),
        ]

    def __str__(self):
        return self.name

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(null=True, verbose_name='Описание')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Продажная цена',
        default=0
    )
    UNITS = [
        ('шт', 'шт'),
        ('кг', 'кг'),
    ]
    discount = models.IntegerField(default=0, verbose_name='Скидка', null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    unit = models.CharField(max_length=2, choices=UNITS, default='шт', verbose_name='Единица измерения', null=True)
    image = models.ImageField(null=True, blank=True, upload_to='products', verbose_name='Изображение')
    bar_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='Штрихкод', unique=True)
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    min_quantity = models.IntegerField(default=0, verbose_name='Минимальный остаток')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bar_code'], name='unique_bar_code', condition=models.Q(bar_code__isnull=False))
        ]
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
    
    def discounted_price(self):
        if self.discount > 0:
            discount_multiplier = Decimal(1) - (Decimal(self.discount) / Decimal(100))
            return self.sale_price * discount_multiplier
        return self.sale_price

    def __str__(self):
        return self.name

    def in_stock(self):
        return self.quantity > 0
    

    def month_sales(self):
        return sum(i.quantity for i in self.soldhistory_set.filter(created__year=datetime.now().year, created__month=datetime.now().month))
