from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from .models import *

admin.site.register(Product)
admin.site.register(Shop)


admin.site.register(Category, MPTTModelAdmin)
