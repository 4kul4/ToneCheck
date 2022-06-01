from django.http import HttpResponse
from django.shortcuts import redirect, render

def index(request):
    return render(request, 'index.html')

def contacts(request):
    return render(request, 'contacts.html')

def login(request):
    return render(request, 'login.html')

def checkin(request):
    return render(request, 'checkin.html')

def status(request):
    return HttpResponse("OK")

