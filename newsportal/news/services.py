from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Subscription, Post
from datetime import datetime, timedelta
from django.contrib.auth.models import User


def send_welcome_email(user):
    """Отправка приветственного письма при регистрации"""
    subject = 'Добро пожаловать на News Portal!'
    html_message = render_to_string('email/welcome_email.html', {
        'user': user,
        'site_url': settings.SITE_URL,
    })

    send_mail(
        subject=subject,
        message='',  # Текстовую версию оставляем пустой, т.к. используем HTML
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_new_post_notification(post):
    """Уведомление подписчиков о новой статье"""
    category = post.categories.first()  # Берем первую категорию для примера
    if not category:
        return

    subscribers = category.get_subscribers()

    for subscriber in subscribers:
        subject = f'Новая статья в категории "{category.name}"'
        html_message = render_to_string('email/new_post_notification.html', {
            'user': subscriber,
            'post': post,
            'category': category,
            'site_url': settings.SITE_URL,
        })

        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=False,
        )


def send_weekly_digest():
    """Еженедельная рассылка новых статей"""
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)

    # Получаем все статьи за последнюю неделю
    recent_posts = Post.objects.filter(
        created_at__gte=week_ago,
        post_type=Post.ARTICLE
    ).order_by('-created_at')

    if not recent_posts:
        return

    # Получаем всех пользователей с подписками
    subscribers = User.objects.filter(
        subscription__isnull=False
    ).distinct()

    for user in subscribers:
        # Получаем категории, на которые подписан пользователь
        user_categories = user.subscription_set.values_list('category', flat=True)

        # Фильтруем статьи по категориям пользователя
        user_posts = recent_posts.filter(categories__in=user_categories).distinct()

        if user_posts:
            subject = 'Еженедельная подборка новых статей'
            html_message = render_to_string('email/weekly_digest.html', {
                'user': user,
                'posts': user_posts,
                'site_url': settings.SITE_URL,
                'week_start': week_ago.date(),
            })

            send_mail(
                subject=subject,
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )