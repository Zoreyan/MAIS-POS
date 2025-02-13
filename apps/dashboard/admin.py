from django.contrib import admin
from .models import *


admin.site.register(Tariff)
admin.site.register(Payment)
admin.site.register(PaymentPeriod)
admin.site.register(Feature)
admin.site.register(Notification)