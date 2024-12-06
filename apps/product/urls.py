from django.urls import path
from .views import *


urlpatterns = [
    path('list/', list_, name='product-list'),
    path('create/', create, name='product-create'),
    path('at_income_create/', product_create, name='product-create-at-income'),
    path('details/<int:pk>/', details, name='product-details'),
    path('update/<int:pk>/', update, name='product-update'),
    path('delete/<int:pk>/', delete, name='product-delete'),
    path('sale/', sale, name='product-sale'),
    path('income/', income, name='product-income'),
    path('get-product/', get_product, name='get-product'),
    path('create-sell-history/', create_sell_history, name='create-sell-history'),
    path('create-income-history/', create_income_history, name='create-income-history'),
    path('update-quantity/', update_quantity, name='update-quantity'),
    path('find-product/', find_product, name='find-product'),
    path('search-product/', search_product, name='search-product'),
    path('category-list/', category_list, name='category-list'),
    path('category-create/', category_create, name='category-create'),
    path('category-delete/<int:pk>/', category_delete, name='category-delete'),
    path('update_category/<int:pk>/', update_category, name='update-category'),
    path('update_category_per_page', update_category_per_page, name='update_category_per_page'),
    path('update_items_per_page', update_items_per_page, name='update_items_per_page')
]