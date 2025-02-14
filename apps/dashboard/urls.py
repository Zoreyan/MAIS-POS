from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('get-top-products-data/', get_top_products_data, name='get-top-products-data'),
    path('get-top-incomes-data/', get_top_incomes_data, name='get-top-incomes-data'),
    path('settings-page/<int:pk>', settings_page, name='settings_page'),

]