from django.shortcuts import render
from django.views.generic import ListView
from .analysis import analysis, get_users
import json
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages


def index_view(request):
    return render(request, 'tweets/index.html')


def search(request):
    if request.method == "POST":
        if 1 == 2:
            username = json.loads(request.body)
            try:
                context = analysis(username)
            except ValueError:
                messages.warning(request, f'The user is not valid')
                return HttpResponseRedirect(reverse_lazy('tweets:tweet-index'))
            return HttpResponseRedirect(reverse_lazy('tweets:tweet-analysis', kwargs={'username': username,
                                                                                      'context': context}), )
        return HttpResponseRedirect(reverse_lazy('tweets:tweet-index'))


def analysis_view(request, username, context):
    return render(request, reverse_lazy('tweets:tweet-user-analysis', kwargs={'username': username}), context)
