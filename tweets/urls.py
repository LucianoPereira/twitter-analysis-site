from django.contrib import admin
from django.urls import path, include
from .views import index_view, search_view, wordcloud_view, info_view
app_name = 'tweets'
urlpatterns = [
    path('', index_view, name='tweets-index'),
    path('search/', search_view, name='search'),
    path('<str:search>/tweets_wordcloud', wordcloud_view,  name='tweets-wordcloud'),
    path('<str:search>/tweets_info', info_view, name='tweets-info'),
]
