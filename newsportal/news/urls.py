from django.urls import path
from . import views

urlpatterns = [
    # Новости
    path('', views.NewsListView.as_view(), name='news_list'),
    path('search/', views.news_search, name='news_search'),
    path('create/', views.NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/', views.post_detail, name='news_detail'),
    path('<int:pk>/edit/', views.NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete/', views.NewsDeleteView.as_view(), name='news_delete'),

    # Статьи
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/', views.post_detail, name='article_detail'),
    path('articles/<int:pk>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('become-author/', views.become_author, name='become_author'),
    path('subscriptions/', views.subscription_management, name='subscription_management'),
    path('subscriptions/toggle/<int:category_id>/', views.toggle_subscription, name='toggle_subscription'),
    path('unsubscribe/category/<int:category_id>/', views.unsubscribe_category, name='unsubscribe_category'),
]