from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('user/', include('apps.user.urls')),
    path('product/', include('apps.product.urls')),
    path('history/', include('apps.history.urls')),
    path('client/', include('apps.client.urls')),
    path('finance/', include('apps.finance.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)