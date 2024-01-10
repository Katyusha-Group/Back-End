from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from chat.models import Chat, Contact

User = get_user_model()


def get_last_10_messages(chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    return Chat.objects.get_20_last_messages(chat.pk)


def get_or_create_user_contact(username):
    user = get_object_or_404(User, username=username)
    return Contact.objects.get_or_create(user=user)[0]


def get_current_chat(chat_id):
    return get_object_or_404(Chat, id=chat_id)
