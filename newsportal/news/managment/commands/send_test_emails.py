from django.core.management.base import BaseCommand
from news.services import send_weekly_digest
from django.contrib.auth.models import User
from news.models import Post

class Command(BaseCommand):
    help = 'Отправка тестовых email для проверки функционала'

    def handle(self, *args, **options):
        # Тест еженедельной рассылки
        send_weekly_digest()
        self.stdout.write(
            self.style.SUCCESS('Еженедельная рассылка отправлена')
        )