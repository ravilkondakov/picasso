from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установим переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bike.settings')

app = Celery('bike')

# Загрузим конфигурацию Django в Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически найдем задачи в проекте
app.autodiscover_tasks()
