from django import template
from apps.product.models import LogEntry

register = template.Library()

@register.simple_tag
def low_stock():
    return LogEntry.objects.filter(action='low_stock_notification').first()