from django.urls import path

from .views import *


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('get-top-products-data/', get_top_products_data, name='get-top-products-data'),
    path('get-top-incomes-data/', get_top_incomes_data, name='get-top-incomes-data'),
]