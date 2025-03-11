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

    tg_id = models.IntegerField(null=True, blank=True, verbose_name='ID в Telegram')

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'