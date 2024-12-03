from django.urls import path
from .views import *


urlpatterns = [
    path('<int:pk>', index, name='shop-index'),
    path('vacancies/<int:pk>', vacancies, name='shop-vacancies'),
    path('about-us/<int:pk>', about_us, name='shop-about-us'),
    path('contacts/<int:pk>', contacts, name='shop-contacts'),
    path('order-list', order_list, name='shop-order-list'),
]