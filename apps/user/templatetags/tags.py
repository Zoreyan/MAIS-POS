from django import template
from django.contrib.auth.models import Permission

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def has_permission(user, permission_codename):
    user_permissions = Permission.objects.filter(user=user)
    return user_permissions.filter(codename=permission_codename).exists()