from django import template
from ..models import Notification

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.simple_tag
def query_transform(request, **kwargs):
    updated = request.GET.copy()
    for key, value in kwargs.items():
        updated[key] = value
    return updated.urlencode()

@register.simple_tag
def notifications(user):
    """Возвращает последние 3 уведомления и количество непрочитанных."""
    if hasattr(user, 'shop'):  # Проверка, что у пользователя есть магазин
        latest_notifications = Notification.objects.filter(shop=user.shop, is_not_read=user).order_by('-id')[:3]
        unread_count = Notification.objects.filter(shop=user.shop, is_not_read=user).count()
        return {'latest_notifications': latest_notifications, 'unread_count': unread_count}
    return {'latest_notifications': [], 'unread_count': 0}