from django.db import models

from decimal import Decimal


class OrderHistory(models.Model):
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, null=True)
    amount = models.FloatField()
    change = models.FloatField(null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)
    profit = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    order_type = models.CharField(max_length=10, choices=[('sale', 'Продажа'), ('income', 'Поступление')], null=True)


    class Meta:
        verbose_name = 'История заказа'
        verbose_name_plural = 'История заказа'

    def total_sum(self):
        total = sum((i.quantity * i.price_at_moment) for i in self.soldhistory_set.all())
        if total == 0:
            total = sum((i.quantity * i.price_at_moment) for i in self.incomehistory_set.all())
        if self.discount:  
            total -= Decimal(self.discount) 
        return total
    
    def total_sum_without_discount(self):
        total = sum((i.quantity * i.price_at_moment) for i in self.soldhistory_set.all())
        return total


class SoldHistory(models.Model):
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(OrderHistory, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    # чтобы сохранить цену товара в момент продажи, если в дальнейшем цена товара изменится 
    # оно не влияет на историю
    price_at_moment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'История продаж'
        verbose_name_plural = 'История продаж'

    def total_sum(self):
        return self.quantity * self.price_at_moment

    def __str__(self):
        return self.product.name


class IncomeHistory(models.Model):
    order = models.ForeignKey(OrderHistory, on_delete=models.CASCADE, null=True)
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    # чтобы сохранить цену товара в момент поставки, если в дальнейшем цена товара изменится 
    # оно не влияет на историю
    price_at_moment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'История поставки'
        verbose_name_plural = 'История поставки'

    def total_sum(self):
        return self.quantity * self.price_at_moment
