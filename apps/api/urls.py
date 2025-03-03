from django.urls import path

from .views import *

urlpatterns = [
    path('get-product/', GetProduct.as_view(), name='get-product'),
    path('get-products/', GetProducts.as_view(), name='get-products'),
]