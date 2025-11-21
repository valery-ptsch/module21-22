from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment, Subscription

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'post_type', 'created_at', 'rating']
    list_filter = ['post_type', 'created_at', 'categories']
    search_fields = ['title', 'content']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at', 'rating']
    list_filter = ['created_at']
    search_fields = ['text']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'subscribed_at']
    list_filter = ['category', 'subscribed_at']
    search_fields = ['user__username', 'category__name']

admin.site.register(PostCategory)