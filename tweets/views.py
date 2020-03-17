from django.shortcuts import render
from django.views.generic import ListView
from .analysis import analysis


def tweet_list(request):
    context = {}
    context['elias'] = 'gato'
    analysis()
    return render(request, 'tweets/index.html', context)
