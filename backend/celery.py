from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем настройки вашего проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Загружаем конфигурацию Celery из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в приложениях
app.autodiscover_tasks()

app.conf.update(
    broker_connection_retry_on_startup=True,
)