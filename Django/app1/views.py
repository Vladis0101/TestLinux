from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


# Create your views here.

def index(request):
    return HttpResponse('Hello')

def hello2(request):

    return HttpResponse('Hello2')