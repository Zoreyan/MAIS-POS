from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import User

@receiver(user_signed_up)
def set_admin_role(request, user, **kwargs):
    """
    Устанавливает роль администратора для новых пользователей после регистрации.
    """
    user.role = 'admin'  # Назначаем роль администратора
    user.save()