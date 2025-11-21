import os
from celery import Celery

# Устанавливаем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')

app = Celery('newsportal')

# Используем строку конфигурации для настроек Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех зарегистрированных приложений Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')