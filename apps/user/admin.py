from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомный админ для модели User
    """
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('shop', 'role', 'phone', 'has_access', 'image', 'tg_id'),
        }),
    )
    list_display = ('username', 'email', 'role', 'shop', 'is_active', 'is_staff', 'has_access')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'shop')

admin.site.register(Notification)