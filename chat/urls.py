# chat/urls.py
from django.urls import path

from django.urls import re_path 
from chat.consumers import ChatConsumer 

from django.urls.conf import include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import *


urlpatterns = [
    re_path(r'room/(?P<room_name>\w+)/$', room, name='room'),
    path('<str:username>/', get_names, name='user-contacts'),
    path('delete/', delete_all_chats, name='del-chats'),
]
