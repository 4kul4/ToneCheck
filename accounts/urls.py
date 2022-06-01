from django.urls import path, re_path

from .views import *
from django_example.web import views

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('log', LoginUser.as_view(), name='log'),
    path('logout', logout_user, name='logout')
]