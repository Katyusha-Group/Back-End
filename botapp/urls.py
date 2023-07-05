from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('get_song/<int:song_id>/', UserViewSet.as_view({'get': 'get_song'})),
    path('get_courses_on_calendar/<int:user_id>/', UserViewSet.as_view({'get': 'get_courses_on_calendar'})),
    path('telegram_link/', TelegramLink.as_view(), name='telegram_link'),
    path('is_it_in_database/', IsItInDatabase.as_view(), name='is_it_in_database'),
    path('get_user_id/<email>/', GetChatIdView.as_view(), name='get_user_id'),
]