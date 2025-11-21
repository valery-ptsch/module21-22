# news/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from allauth.account.signals import user_signed_up
from .models import Post
from .services import send_welcome_email, send_new_post_notification

@receiver(user_signed_up)
def user_signed_up_receiver(request, user, **kwargs):
    """Отправка приветственного письма при регистрации"""
    send_welcome_email(user)

@receiver(post_save, sender=Post)
def post_created_receiver(sender, instance, created, **kwargs):
    """Уведомление подписчиков о новой статье"""
    if created and instance.post_type == Post.ARTICLE:
        send_new_post_notification(instance)