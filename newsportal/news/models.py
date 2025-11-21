from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone



class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Суммарный рейтинг каждой статьи автора умножается на 3
        posts_rating = self.post_set.aggregate(pr=Sum('rating'))['pr'] or 0
        posts_rating *= 3

        # Суммарный рейтинг всех комментариев автора
        comments_rating = self.user.comment_set.aggregate(cr=Sum('rating'))['cr'] or 0

        # Суммарный рейтинг всех комментариев к статьям автора
        posts_comments_rating = Comment.objects.filter(post__author=self).aggregate(pcr=Sum('rating'))['pcr'] or 0

        self.rating = posts_rating + comments_rating + posts_comments_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_subscribers(self):
        """Получить всех подписчиков категории"""
        return User.objects.filter(subscription__category=self)


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.post_type == self.NEWS:
            return reverse('news_detail', args=[str(self.id)])
        else:
            return reverse('article_detail', args=[str(self.id)])

    def get_absolute_url(self):
        from django.conf import settings
        return f"{settings.SITE_URL}{reverse('news_detail', args=[str(self.id)])}"

    def notify_subscribers(self):
        """Уведомление подписчиков о новой статье"""
        from .services import send_new_post_notification
        if self.post_type == self.ARTICLE:  # Уведомляем только о статьях
            send_new_post_notification(self)


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f"Комментарий от {self.user.username} к {self.post.title}"

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Категория')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        unique_together = ('user', 'category')  # Одна подписка на категорию для пользователя
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user.username} - {self.category.name}"

    @receiver(post_save, sender=User)
    def send_welcome_email(sender, instance, created, **kwargs):
        """Отправка приветственного письма при регистрации"""
        if created and instance.email:
            try:
                subject = 'Добро пожаловать в News Portal!'

                html_message = render_to_string('email/welcome_email.html', {
                    'user': instance,
                })

                plain_message = f"""
                Добро пожаловать в News Portal, {instance.username}!

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
                    recipient_list=[instance.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Ошибка отправки приветственного письма: {e}")

    @receiver(m2m_changed, sender=Post.categories.through)
    def notify_subscribers(sender, instance, action, **kwargs):
        """Уведомление подписчиков при добавлении статьи в категорию"""
        if action == "post_add" and instance.post_type == Post.ARTICLE:
            from .tasks import send_post_notification
            # Откладываем отправку уведомлений на 10 секунд, чтобы пост успел сохраниться
            send_post_notification.apply_async([instance.id], countdown=10)