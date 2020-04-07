from django.shortcuts import render
import pandas as pd
from django.views.generic import ListView
import json
from django.http import Http404
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
    save_tweet_wordcloud,
    prepare_wordcloud_data,
    bag_of_words_from_tweets,
)
from .ml_models import (
    lda_model,
    lda_topics_wc,
    )
from .tweepy import authenticate_api


def index_view(request):
    return render(request, 'tweets/index.html')


def search_view(request):
    if request.POST['search']:
        if 'wordcloud' in request.POST:
            return HttpResponseRedirect(
                reverse_lazy('tweets:tweets-wordcloud', kwargs={'search': request.POST['search']}))
        elif 'tweets_info' in request.POST:
            return HttpResponseRedirect(reverse_lazy('tweets:tweets-info', kwargs={'search': request.POST['search']}))
        elif 'topics' in request.POST:
            return HttpResponseRedirect(reverse_lazy('tweets:tweets-topics', kwargs={'search': request.POST['search']}))
    return HttpResponseRedirect(reverse_lazy('tweets:tweets-index'))


def wordcloud_view(request, search):
    username = search
    api = authenticate_api()
    try:
        df = tweets_dataframe(search, api, 500)
    except Http404:
        messages.warning(request, f'The user is not valid')
        return HttpResponseRedirect(reverse_lazy('tweets:tweets-index'))
    name = df['user.name'][0]
    screen_name = df['user.screen_name'][0]
    df_text = df['full_text']
    tweet_list = df_text.apply(cleanup)
    tweet_text = prepare_wordcloud_data(tweet_list)
    save_tweet_wordcloud(tweet_text, 'static/tweets/wordcloud.jpg', 'twitter11.png')
    context = {
        'name': name,
        'screen_name': screen_name,
    }
    return render(request, 'tweets/tweets_wordcloud.html', context)


def info_view(request, search):
    api = authenticate_api()
    try:
        df = tweets_dataframe(search, api, 500)
    except Http404:
        messages.warning(request, f'The user is not valid')
        return HttpResponseRedirect(reverse_lazy('tweets:tweets-index'))
    name = df['user.name'][0]
    screen_name = df['user.screen_name'][0]
    most_liked_tweets = get_most_liked_tweets(df, 5)
    most_retweeted_tweets = get_most_retweeted_tweets(df, 5)
    most_mentioned_dict = get_most_mentioned_dict(df_to_tweet_list(df), 15)
    context = {
        'name': name,
        'screen_name': screen_name,
        'most_liked_tweets': most_liked_tweets,
        'most_retweeted_tweets': most_retweeted_tweets,
        'most_mentioned_dict': most_mentioned_dict,
    }
    return render(request, 'tweets/tweets_info.html', context)


def topics_view(request, search):
    api = authenticate_api()
    try:
        df = tweets_dataframe(search, api, 500)
    except Http404:
        messages.warning(request, f'The user is not valid')
        return HttpResponseRedirect(reverse_lazy('tweets:tweets-index'))
    name = df['user.name'][0]
    screen_name = df['user.screen_name'][0]
    df_text = df['full_text']
    tweet_list = df_text.apply(cleanup)
    tweet_bow, tf_feature_names = bag_of_words_from_tweets(tweet_list)
    topic_amount = 3

    lda_z, lda = lda_model(tweet_bow, topic_amount)
    n_top_words = 40
    lda_topic_list = lda_topics_wc(lda, tf_feature_names)
    routes = []
    for i, item in enumerate(lda_topic_list):
        routes.append('static/tweets/topic{}.jpg'.format(i))
        save_tweet_wordcloud(item, routes[i])
    routes = [route.replace('static/', '') for route in routes]
    context = {
        'name': name,
        'screen_name': screen_name,
        'topic_amt': topic_amount,
        'routes': routes,
    }
    return render(request, 'tweets/topics.html', context)
