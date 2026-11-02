from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def dashboard_health(request):
    return HttpResponse("Hello, this is the dashboard health check endpoint.")
