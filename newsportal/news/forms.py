from django import forms
from .models import Post, Category, Author
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group




class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='Имя', required=False)
    last_name = forms.CharField(max_length=30, label='Фамилия', required=False)

    def save(self, request):
        user = super().save(request)

        # Добавляем пользователя в группу common
        common_group = Group.objects.get(name='common')
        user.groups.add(common_group)

        # Сохраняем дополнительные поля
        if self.cleaned_data['first_name']:
            user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data['last_name']:
            user.last_name = self.cleaned_data['last_name']
        user.save()

        return user


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
        }


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='Имя', required=False)
    last_name = forms.CharField(max_length=30, label='Фамилия', required=False)

    def save(self, request):
        user = super().save(request)

        # Добавляем пользователя в группу common
        common_group = Group.objects.get(name='common')
        user.groups.add(common_group)

        # Сохраняем дополнительные поля
        if self.cleaned_data['first_name']:
            user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data['last_name']:
            user.last_name = self.cleaned_data['last_name']
        user.save()

        return user