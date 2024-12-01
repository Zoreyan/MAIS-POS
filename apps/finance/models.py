from django.db import models


class Expense(models.Model):
    CHOICES = [
        ('rent', 'Аренда'),
        ('utilities', 'Коммунальные услуги'),
        ('salaries', 'Зарплаты'),
        ('other', 'Другое')
    ]
    image = models.ImageField(null=True, blank=True, upload_to='expenses', verbose_name="Изображение")
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, verbose_name="Магазин", null=True, blank=True)
    type = models.CharField(max_length=50, choices=CHOICES, verbose_name="Тип расхода")
    description = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    created = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.type