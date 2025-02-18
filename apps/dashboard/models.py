from django.db import models

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