# check_setup.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

from django.conf import settings

print("=== ПРОВЕРКА НАСТРОЕК ===")

# Проверка apps
required_apps = [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

for app in required_apps:
    status = "✅" if app in settings.INSTALLED_APPS else "❌"
    print(f"{status} {app}")

# Проверка middleware
required_middleware = 'allauth.account.middleware.AccountMiddleware'
status = "✅" if required_middleware in settings.MIDDLEWARE else "❌"
print(f"{status} {required_middleware}")

# Проверка SITE_ID
print(f"✅ SITE_ID: {getattr(settings, 'SITE_ID', 'НЕ НАЙДЕН')}")

print("\n=== КОМАНДЫ ДЛЯ ЗАПУСКА ===")
print("1. python manage.py migrate")
print("2. python manage.py createsuperuser")
print("3. python manage.py runserver")