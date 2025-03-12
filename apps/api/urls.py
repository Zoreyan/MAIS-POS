from django.urls import path

from .views import *

urlpatterns = [
    path('get-product/', GetProduct.as_view(), name='get-product'),
    path('get-products/', GetProducts.as_view(), name='get-products'),
    path('check-user-exists/', CheckUserExists.as_view(), name='check-user-exists'),
    path('auth/', AuthView.as_view(), name='auth'),
    path('create-payment/', PaymentCreateView.as_view(), name='create-payment'),
    path('check-payment-status/', CheckPaymentStatusView.as_view(), name='check-payment-status'),
]

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'sales', TodayRevenue, basename='sales')