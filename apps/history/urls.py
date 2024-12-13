from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # История
    path('total/', total, name='total'),
    path('sold-history/', sales, name='sold-history'),
    path('income-history/', incomes, name='income-history'),
    path('sold-history-delete/<int:pk>/', sales_delete, name='sold-history-delete'),
    path('income-history-delete/<int:pk>/', income_delete, name='income-history-delete'),
    path('order-history-delete/<int:pk>/', order_delete, name='order-history-delete'),

    path('update_orders_per_page', update_orders_per_page, name='update_orders_per_page'),
    path('update_sales_per_page', update_sales_per_page, name='update_sales_per_page'),
    path('update_incomes_per_page', update_incomes_per_page, name='update_incomes_per_page'),
]