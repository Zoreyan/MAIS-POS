from django.db import models
import uuid
from .tasks import send_telegram_message

class OrderHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('online', 'Онлайн'),
        ('split', 'Разделенно'),
    ]

    user = models.ForeignKey('user.User', on_delete=models.CASCADE, null=True)
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, null=True)
    cash_payment = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    online_payment = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    change = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True, default=0)
    discount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.user} - {self.created}'
    
    def total_sum(self):
        return self.cash_payment + self.online_payment
    
    def subtotal_sum(self):
        return self.total_sum() - self.change - self.discount

    class Meta:
        verbose_name = 'История заказа'
        verbose_name_plural = 'История заказа'


class SoldHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(OrderHistory, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'История продаж'
        verbose_name_plural = 'История продаж'
    
    def __str__(self):
        return f'{self.id} - {self.product} - {self.created}'
    
    def total_sum(self):
        return self.quantity * self.amount



class IncomeHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'История поставки'
        verbose_name_plural = 'История поставки'

    def __str__(self):
        return f'{self.id} - {self.product} - {self.created}'
    
    def total_sum(self):
        return self.quantity * self.amount
    


class LogHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, null=True)    
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, null=True)
    message = models.TextField(null=True, blank=True)
    object = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем объект
        send_telegram_message.delay(self.user.tg_id, f"📌 Новый лог:\n👤 Ответственный: {self.user.first_name}\n💬 Сообщение: {self.message}\n📦 Объект: {self.object}")  # Потом отправляем уведомление

    class Meta:
        verbose_name = 'История логов'
        verbose_name_plural = 'История логов'
    
    def __str__(self):
        return f'{self.id} - {self.user} - {self.created}'