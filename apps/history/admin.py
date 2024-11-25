from django.contrib import admin

from .models import *


admin.site.register(SoldHistory)
admin.site.register(IncomeHistory)
admin.site.register(OrderHistory)