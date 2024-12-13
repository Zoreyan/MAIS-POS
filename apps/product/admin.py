from django.contrib import admin
from .models import *
from mptt.admin import MPTTModelAdmin


admin.site.register(Product)
admin.site.register(Shop)


admin.site.register(Category, MPTTModelAdmin)