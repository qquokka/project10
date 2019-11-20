from django.shortcuts import render
from django.contrib.auth import get_user_model

def index(request):
    context = {
        'users' : get_user_model().objects.all()
    }
    return render(request, 'accounts/index.html', context)

def detail(request, user_pk):
    context = {
        'user' : get_user_model().objects.get(pk=user_pk)
    }
    return render(request, 'accounts/detail.html', context)