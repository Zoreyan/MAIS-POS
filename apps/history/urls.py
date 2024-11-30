from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # История
    path('history/', history, name='history'),
    path('sold-history/', sales, name='sold-history'),
    path('income-history/', incomes, name='income-history'),
    path('sold-history-delete/<int:pk>/', sales_delete, name='sold-history-delete'),
    path('income-history-delete/<int:pk>/', incomes_delete, name='income-history-delete'),
    path('order-history-delete/<int:pk>/', order_delete, name='order-history-delete'),
]