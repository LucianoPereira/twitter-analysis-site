from django.shortcuts import render
import pandas as pd
from django.views.generic import ListView
import json
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Search
from .data_manipulation import (
    tweets_dataframe,
    cleanup,
    get_most_liked_tweets,
    get_most_retweeted_tweets,
    get_most_mentioned_dict,
    df_to_tweet_list,
)
from .tweepy import authenticate_api


def index_view(request):
    return render(request, 'tweets/index.html')


def search_view(request):
    return HttpResponseRedirect(reverse_lazy('tweets:tweets-wordcloud', kwargs={'search': request.POST['search']}))


def wordcloud_view(request, search):
    username = search
    try:
        pass
    except ValueError:
        messages.warning(request, f'The user is not valid')
        return HttpResponseRedirect(reverse_lazy('tweets:tweet-index'))
    context = {}
    return render(request, 'tweets_wordcloud.html', context)


def info_view(request, search):
    api = authenticate_api()
    df = tweets_dataframe(search, api, 200)
    name = df['user.name']
    screen_name = df['user.screen_name']
    most_liked_tweets = get_most_liked_tweets(df, 5)
    most_retweeted_tweets = get_most_retweeted_tweets(df, 5)
    most_mentioned_dict = get_most_mentioned_dict(df_to_tweet_list(df), 15)
    context = {
        'name': name,
        'scren_name': screen_name ,
        'most_liked_tweets': most_liked_tweets,
        'most_retweeted_tweets': most_retweeted_tweets,
        'most_mentioned_dict': most_mentioned_dict,
    }
    return render(request, 'tweets/tweets_info.html', context)
