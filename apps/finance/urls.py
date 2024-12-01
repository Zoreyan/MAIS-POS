from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', list, name='finance-list'),
    path('create/', create, name='finance-create'),
]