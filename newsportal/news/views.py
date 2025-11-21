from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from .models import Post, Category, Subscription
from .filters import PostFilter
from .forms import PostForm
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import Author
from .mixins import AuthorsOnlyMixin, AuthorRequiredMixin
from django.http import JsonResponse

class NewsListView(ListView):
    model = Post
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Post.objects.filter(post_type=Post.NEWS)
        return queryset


class ArticleListView(ListView):
    model = Post
    template_name = 'news/article_list.html'
    context_object_name = 'article_list'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Post.objects.filter(post_type=Post.ARTICLE)
        return queryset


def news_search(request):
    news_list = Post.objects.filter(post_type=Post.NEWS).order_by('-created_at')

    # Применяем фильтры
    news_filter = PostFilter(request.GET, queryset=news_list)
    filtered_news = news_filter.qs

    # Пагинация
    paginator = Paginator(filtered_news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'filter': news_filter,
        'page_obj': page_obj,
    }

    return render(request, 'news/news_search.html', context)


class PostDetailView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'


# Базовый класс для проверки авторства
class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author.user


# Создание новости
class NewsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/news_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user.author
        form.instance.post_type = Post.NEWS
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news_detail', kwargs={'pk': self.object.pk})


# Редактирование новости
class NewsUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/news_form.html'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)

    def get_success_url(self):
        return reverse_lazy('news_detail', kwargs={'pk': self.object.pk})


# Удаление новости
class NewsDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news_list')
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)

    def form_valid(self, form):
        messages.success(self.request, 'Новость успешно удалена')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление новости'
        return context


# Создание статьи
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/article_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user.author
        form.instance.post_type = Post.ARTICLE
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.object.pk})


# Редактирование статьи
class ArticleUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news/article_form.html'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)

    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.object.pk})


# Удаление статьи
class ArticleDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)

    def form_valid(self, form):
        messages.success(self.request, 'Статья успешно удалена')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление статьи'
        return context


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    context = {'post': post}
    return render(request, 'news/post_detail.html', context)


@login_required
def become_author(request):
    """Представление для добавления пользователя в группу authors"""
    if request.method == 'POST':
        authors_group = Group.objects.get(name='authors')
        request.user.groups.add(authors_group)

        # Создаем профиль автора, если его нет
        if not hasattr(request.user, 'author'):
            Author.objects.create(user=request.user)

        messages.success(request, 'Поздравляем! Теперь вы автор и можете публиковать новости и статьи.')
        return redirect('news_list')

    return render(request, 'news/become_author.html')


@login_required
def subscription_management(request):
    """Управление подписками пользователя"""
    categories = Category.objects.all()
    user_subscriptions = Subscription.objects.filter(user=request.user)
    subscribed_category_ids = user_subscriptions.values_list('category_id', flat=True)

    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        action = request.POST.get('action')

        category = get_object_or_404(Category, id=category_id)

        if action == 'subscribe':
            Subscription.objects.get_or_create(user=request.user, category=category)
            messages.success(request, f'Вы подписались на категорию "{category.name}"')
        elif action == 'unsubscribe':
            Subscription.objects.filter(user=request.user, category=category).delete()
            messages.success(request, f'Вы отписались от категории "{category.name}"')

        return redirect('subscription_management')

    context = {
        'categories': categories,
        'subscribed_category_ids': list(subscribed_category_ids),
    }
    return render(request, 'news/subscription_management.html', context)


@login_required
def toggle_subscription(request, category_id):
    """Переключение подписки на категорию"""
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)

        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            category=category
        )

        if created:
            message = f'Вы подписались на категорию "{category.name}"'
            messages.success(request, message)
        else:
            subscription.delete()
            message = f'Вы отписались от категории "{category.name}"'
            messages.success(request, message)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'subscribed': created,
                'message': message
            })

        return redirect('manage_subscriptions')

    return redirect('manage_subscriptions')


@login_required
def unsubscribe_category(request, category_id):
    """Отписка от категории"""
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        Subscription.objects.filter(user=request.user, category=category).delete()
        messages.success(request, f'Вы отписались от категории "{category.name}"')
        return redirect('manage_subscriptions')

    category = get_object_or_404(Category, id=category_id)
    return render(request, 'news/unsubscribe_confirm.html', {
        'category': category
    })