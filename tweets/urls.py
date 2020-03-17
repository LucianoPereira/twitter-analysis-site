from django.contrib import admin
from django.urls import path, include
from .views import tweet_list
app_name = 'tweets'
urlpatterns = [
    path('', tweet_list, name='tweet-index'),
]
