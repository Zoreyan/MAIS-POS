from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.product.models import Shop


class User(AbstractUser):
    """
    Модель пользователя
    """
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        verbose_name='Магазин',
        null=True
    )

    image = models.ImageField(
        null=True,
        verbose_name='Фото',
        upload_to='user_images/',
        default='user_images/default_user.png',
        blank=True
    )

    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('cashier', 'Кассир'),
        ('owner', 'Владелец'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='admin',
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Телефон'
    )

    has_access = models.BooleanField(
        default=False,
        verbose_name='Доступ'
    )

    get_email_notification = models.BooleanField(
        default=True,
        verbose_name='Получать уведомления через email'
    )

    tg_id = models.IntegerField(null=True, blank=True, verbose_name='ID в Telegram')

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'
    
class Notification(models.Model):
    shop = models.ForeignKey('product.Shop', on_delete=models.CASCADE, verbose_name="Магазин")
    category = models.CharField(max_length=100, verbose_name="Тип уведомления")
    title = models.CharField(max_length=100, verbose_name="Название уведомления")
    details = models.TextField(verbose_name="Описание уведомления")
    is_not_read = models.ManyToManyField('User', verbose_name="Не прочитано")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True, blank=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def unread_count(self):
        """Возвращает количество непрочитанных уведомлений для текущего пользователя."""
        return self.is_not_read.count()