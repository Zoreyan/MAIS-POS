from django.db import models



class Tariff(models.Model):
    sequence = models.IntegerField(verbose_name="Порядковый номер", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="Название тарифа")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    help_text = models.TextField(verbose_name="Дополнения", null=True, blank=True)
    avaliable = models.BooleanField(default=True, verbose_name="Доступен")


    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self):
        return self.name

class Feature(models.Model):
    tariff = models.ForeignKey('Tariff', on_delete=models.CASCADE, related_name='features', verbose_name="Тариф", default=1)
    sequence = models.IntegerField(verbose_name="Порядковый номер", null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name="Название функции")
    status = models.BooleanField(default=True, verbose_name="Статус")


    class Meta:
        verbose_name = "Функция тарифа"
        verbose_name_plural = "Функции тарифа"

    def __str__(self):
        return f"{self.name} ({self.tariff.name}) - {self.status}"

class Payment(models.Model):
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, verbose_name="Магазин")
    tariff = models.ForeignKey('Tariff', on_delete=models.CASCADE, verbose_name="Тариф")
    period = models.ForeignKey('PaymentPeriod', on_delete=models.CASCADE, verbose_name="Период оплаты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"

    def __str__(self):
        return f"Оплата {self.shop.name} - {self.tariff.name} ({self.period.duration} дней)"

class PaymentPeriod(models.Model):
    duration = models.PositiveIntegerField(verbose_name="Период оплаты (в днях)")
    description = models.TextField(verbose_name="Описание периода (месяц, 12 месяцев, год)", null=True, blank=True)
    discount = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        verbose_name="Скидка (%)",
        help_text="Скидка в процентах, например 10.00 для 10%."
    )

    class Meta:
        verbose_name = "Период оплаты"
        verbose_name_plural = "Периоды оплат"

    def __str__(self):
        return f"{self.duration} дней - Скидка {self.discount}%"

class Notification(models.Model):
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, verbose_name="Магазин")
    category = models.CharField(max_length=100, verbose_name="Тип уведомления")
    title = models.CharField(max_length=100, verbose_name="Название уведомления")
    details = models.TextField(verbose_name="Описание уведомления")
    is_not_read = models.ManyToManyField('user.User', verbose_name="Не прочитано")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True, blank=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def unread_count(self):
        """Возвращает количество непрочитанных уведомлений для текущего пользователя."""
        return self.is_not_read.count()