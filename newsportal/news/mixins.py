# news/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AuthorsOnlyMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является автором"""
    permission_required = 'news.add_post'

    def test_func(self):
        return self.request.user.groups.filter(name='authors').exists()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied("У вас нет прав для выполнения этого действия. Станьте автором!")
        return super().handle_no_permission()


class AuthorRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является автором конкретного поста"""

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author.user

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied("Вы не являетесь автором этого поста")
        return super().handle_no_permission()