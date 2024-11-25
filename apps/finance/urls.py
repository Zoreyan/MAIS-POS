from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', finance_list, name='finance-list'),
    path('create/', create, name='expend-create'),
    path('get-chart-data-finance/', get_chart_data, name='get-chart-data-finance'),
    path('expends/', expends, name='expends'),
    path('extends_chart/', extends_chart_data, name='extends-chart-data'),
    path('update/<int:pk>/', expend_update, name='expend-update'),
    path('delete/<int:pk>/', expend_delete, name='expend-delete'),
    path('salaries/', salary_list, name='salary-list'),
]