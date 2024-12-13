from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', finance_list, name='finance-list'),
    path('create/', create, name='finance-create'),
    path('delete/<int:pk>/', expense_delete, name='expense-delete'),
    path('update_finance_per_page', update_finance_per_page, name='update_finance_per_page'),
]