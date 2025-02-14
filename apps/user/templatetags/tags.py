from django import template
from django.contrib.auth.models import Permission
from apps.dashboard.models import Notification


register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def has_permission(user, permission_codename):
    user_permissions = Permission.objects.filter(user=user)
    return user_permissions.filter(codename=permission_codename).exists()

@register.filter
def shop_balance(user):
    """Возвращает баланс магазина пользователя, если магазин существует."""
    return user.shop.balance if hasattr(user, 'shop') else 0

@register.simple_tag
def notifications(user):
    """Возвращает последние 3 уведомления и количество непрочитанных."""
    if hasattr(user, 'shop'):  # Проверка, что у пользователя есть магазин
        latest_notifications = Notification.objects.filter(shop=user.shop, is_not_read=user).order_by('-id')[:3]
        unread_count = Notification.objects.filter(shop=user.shop, is_not_read=user).count()
        return {'latest_notifications': latest_notifications, 'unread_count': unread_count}
    return {'latest_notifications': [], 'unread_count': 0}  # Если нет магазина, возвращаем пустые данные