<<<<<<< HEAD
from django.db import models
from datetime import datetime
from mptt.models import MPTTModel, TreeForeignKey


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

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Продажная цена'
    )
    UNITS = [
        ('шт', 'шт'),
        ('кг', 'кг'),
    ]
    unit = models.CharField(max_length=2, choices=UNITS, default='шт', verbose_name='Единица измерения', null=True)
    image = models.ImageField(null=True, blank=True, upload_to='products', verbose_name='Изображение')
    bar_code = models.CharField(max_length=100, null=True, verbose_name='Штрихкод', unique=True)
    quantity = models.IntegerField(default=0, verbose_name='Количество')
    min_quantity = models.IntegerField(default=0, verbose_name='Минимальный остаток')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name

    def in_stock(self):
        return self.quantity > 0
    

    def month_sales(self):
        return sum(i.quantity for i in self.soldhistory_set.filter(created__year=datetime.now().year, created__month=datetime.now().month))

=======
from django.db import models
from datetime import datetime
from mptt.models import MPTTModel, TreeForeignKey


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
    image = models.ImageField(null=True, blank=True, upload_to='shops', verbose_name='Изображение')
    name = models.CharField(max_length=100, verbose_name='Название')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Продажная цена'
    )
    UNITS = [
        ('шт', 'шт'),
        ('кг', 'кг'),
    ]
    unit = models.CharField(max_length=2, choices=UNITS, default='шт', verbose_name='Единица измерения', null=True)
    image = models.ImageField(null=True, blank=True, upload_to='products', verbose_name='Изображение')
    bar_code = models.CharField(max_length=100, null=True, verbose_name='Штрихкод', unique=True)
    quantity = models.IntegerField(default=0, verbose_name='Количество')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name

    def in_stock(self):
        return self.quantity > 0
    

    def month_sales(self):
        return sum(i.quantity for i in self.soldhistory_set.filter(created__year=datetime.now().year, created__month=datetime.now().month))

>>>>>>> 0f5feb102b45a94eef3b618ce0c3188881e35ea1
