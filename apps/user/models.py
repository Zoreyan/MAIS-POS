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
    email = models.EmailField(
        unique=True,
        verbose_name='Почта',
    )
    
    image = models.ImageField(
        null=True,
        verbose_name='Фото',
        upload_to='user_images/',
        default='user_images/default_user.png',
        blank=True
    )

    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
        ('cashier', 'Кассир'),
        ('client', 'Клиент'),
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

    access = models.BooleanField(
        default=False,
        verbose_name='Доступ'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def have_access():
        if self.role == 'owner' and self.access == True or self.is_superuser:
            return True
        else:
            return False

    def __str__(self):
        return f'{self.username}'