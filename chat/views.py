from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from chat.models import Chat, Contact
from chat.scripts.chat_views import get_or_create_user_contact
from .serializers import ChatSerializer, CreateChatSerializer, ChatRetrieveSerializer

User = get_user_model()


# TODO: Add contacts viewset later


class ChatViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Chat.objects.all()
        contact = Contact.objects.get(user=self.request.user)
        queryset = contact.chats.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateChatSerializer
        elif self.action == 'retrieve':
            return ChatRetrieveSerializer
        return ChatSerializer
