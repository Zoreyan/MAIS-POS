from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('list/', list_, name='product-list'),
    path('start-csv-import/', start_csv_import, name='start-csv-import'),
    path('check-csv-import-status/', check_csv_import_status, name='check-csv-import-status'),
    path('create/', create, name='product-create'),
    path('update/<uuid:pk>/', update, name='product-update'),
    path('delete/<uuid:pk>/', delete, name='product-delete'),
    path('sale/', sale, name='product-sale'),
    path('income/', income, name='product-income'),
    path('create-sale-history/', create_sale_history, name='create-sale-history'),
    path('category-list/', category_list, name='category-list'),
    path('category-update/<uuid:pk>/', category_update, name='category-update'),
    path('category-delete/<uuid:pk>/', category_delete, name='category-delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
