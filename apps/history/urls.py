from django.urls import path
from .views import *


urlpatterns = [
    # История
    path('total/', total, name='total'),
    path('sold-history/', sales, name='sold-history'),
    path('income-history/', incomes, name='income-history'),
    path('sold-history-delete/<uuid:pk>/', sales_delete, name='sold-history-delete'),
    path('income-history-delete/<uuid:pk>/', income_delete, name='income-history-delete'),
    path('order-history-delete/<uuid:pk>/', order_delete, name='order-history-delete'),
    path('log-history/', log_list, name='log-history'),
    path('receipt/<uuid:pk>/', receipt, name='receipt'),
    path('select_all_orders', select_all_orders, name='select-all-orders'),
    path('delete_orders', delete_orders, name='delete-orders'),
    path('export_orders', export_orders, name='export-orders'),
]