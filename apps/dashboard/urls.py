from django.urls import path
from .views import *


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('get-chart-data/', get_chart_data, name='get-chart-data'),
    path('settings/', settings, name='settings'),
]