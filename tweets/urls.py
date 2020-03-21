from django.contrib import admin
from django.urls import path, include
from .views import index_view, search, analysis_view
app_name = 'tweets'
urlpatterns = [
    path('', index_view, name='tweet-index'),
    path('search/', search, name='search'),
    path('user=<str:username>/analysis', analysis_view,  name='tweet-user-analysis')
]
