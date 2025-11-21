from django.apps import AppConfig

class NewsConfig(AppConfig):
    name = 'news'

    def ready(self):
        # Импортируем и регистрируем сигналы
        from . import signals

        # Запускаем планировщик только в основном процессе
        import os
        if os.environ.get('RUN_MAIN'):
            from .scheduler import start_scheduler
            start_scheduler()