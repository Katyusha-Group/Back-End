from django.conf.urls import url
from django.urls import re_path

from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_id>\w+)/$", ChatConsumer.as_asgi()),
]
