from celery import shared_task
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Post, Category, Subscription
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_post_notification(post_id):
    """
    Отправка уведомлений подписчикам о новой статье
    """
    try:
        post = Post.objects.get(id=post_id)

        # Проверяем, что это статья и уведомления еще не отправлялись
        if post.post_type != Post.ARTICLE or post.notification_sent:
            return f"Уведомления для статьи {post_id} не требуются"

        # Получаем категории статьи
        categories = post.categories.all()

        if not categories:
            return f"Статья {post_id} не имеет категорий"

        # Собираем всех подписчиков этих категорий
        subscribers_emails = set()
        for category in categories:
            subscriptions = Subscription.objects.filter(category=category).select_related('user')
            for subscription in subscriptions:
                if subscription.user.email:
                    subscribers_emails.add(subscription.user.email)

        if not subscribers_emails:
            return f"Нет подписчиков для категорий статьи {post_id}"

        # Формируем email
        subject = f'Новая статья: {post.title}'

        html_message = render_to_string('email/new_article_notification.html', {
            'post': post,
            'categories': categories,
            'site_url': 'http://127.0.0.1:8000',
        })

        plain_message = f"""
        Новая статья в категории {', '.join([cat.name for cat in categories])}

        {post.title}

        {post.preview()}

        Читать полностью: http://127.0.0.1:8000{post.get_absolute_url()}

        ---
        News Portal
        """

        # Отправляем email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(subscribers_emails),
            html_message=html_message,
            fail_silently=False,
        )

        # Помечаем статью как обработанную
        post.notification_sent = True
        post.save()

        logger.info(f"Уведомления для статьи {post_id} отправлены {len(subscribers_emails)} подписчикам")
        return f"Успешно отправлено {len(subscribers_emails)} уведомлений"

    except Post.DoesNotExist:
        logger.error(f"Статья {post_id} не найдена")
        return f"Статья {post_id} не найдена"
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {str(e)}")
        return f"Ошибка: {str(e)}"


@shared_task
def send_weekly_newsletter():
    """
    Еженедельная рассылка новых статей
    """
    try:
        # Дата неделю назад
        one_week_ago = timezone.now() - timedelta(days=7)

        # Получаем все статьи за последнюю неделю
        recent_articles = Post.objects.filter(
            post_type=Post.ARTICLE,
            created_at__gte=one_week_ago
        ).order_by('-created_at')

        if not recent_articles:
            return "За последнюю неделю не было новых статей"

        # Группируем статьи по категориям
        articles_by_category = {}
        for article in recent_articles:
            for category in article.categories.all():
                if category.id not in articles_by_category:
                    articles_by_category[category.id] = {
                        'category': category,
                        'articles': []
                    }
                articles_by_category[category.id]['articles'].append(article)

        # Для каждой категории отправляем подписчикам
        total_sent = 0
        for category_data in articles_by_category.values():
            category = category_data['category']
            articles = category_data['articles']

            # Получаем подписчиков категории
            subscribers = User.objects.filter(
                subscriptions__category=category,
                email__isnull=False
            ).distinct()

            if not subscribers:
                continue

            for subscriber in subscribers:
                subject = f'Еженедельная подборка статей в категории "{category.name}"'

                html_message = render_to_string('email/weekly_newsletter.html', {
                    'subscriber': subscriber,
                    'category': category,
                    'articles': articles,
                    'site_url': 'http://127.0.0.1:8000',
                })

                plain_message = f"""
                Еженедельная подборка статей в категории "{category.name}"

                Новые статьи за неделю:
                {chr(10).join([f"- {article.title}: http://127.0.0.1:8000{article.get_absolute_url()}" for article in articles])}

                Всего новых статей: {len(articles)}

                ---
                News Portal
                """

                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                total_sent += 1

        logger.info(f"Еженедельная рассылка отправлена {total_sent} подписчикам")
        return f"Еженедельная рассылка отправлена {total_sent} подписчикам"

    except Exception as e:
        logger.error(f"Ошибка при еженедельной рассылке: {str(e)}")
        return f"Ошибка: {str(e)}"


@shared_task
def send_welcome_email_task(user_id):
    """
    Задача для отправки приветственного письма
    """
    try:
        user = User.objects.get(id=user_id)

        subject = 'Добро пожаловать в News Portal!'

        html_message = render_to_string('email/welcome_email.html', {
            'user': user,
        })

        plain_message = f"""
        Добро пожаловать в News Portal, {user.username}!

        Мы рады приветствовать вас в нашем сообществе.

        Теперь вы можете:
        - Читать новости и статьи
        - Подписываться на интересующие категории
        - Получать уведомления о новых публикациях
        - Комментировать материалы

        Приятного использования!

        С уважением,
        Команда News Portal
        """

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return f"Приветственное письмо отправлено {user.email}"

    except User.DoesNotExist:
        return "Пользователь не найден"
    except Exception as e:
        return f"Ошибка: {str(e)}"