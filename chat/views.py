from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from chat.models import Chat, Contact
from chat.scripts.chat_views import get_or_create_user_contact
from .serializers import ChatSerializer, CreateChatSerializer, ChatRetrieveSerializer, MessageSerializer

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
        if self.request.user.is_anonymous:
            return Chat.objects.none()
        contact = Contact.objects.get_or_create(user=self.request.user)[0]
        queryset = contact.chats.all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateChatSerializer
        elif self.action == 'retrieve':
            return ChatRetrieveSerializer
        return ChatSerializer

    @action(
        detail=False,
        methods=['get', 'post'],
        url_path=r'index',
        url_name='chat_index',
    )
    def index(self, request):
        return render(request, 'chat/index.html')

    @action(
        detail=True,
        methods=['get', 'post'],
        url_path=r'room',
        url_name='chat_room',
    )
    def room(self, request, pk):
        chat = self.get_object()
        if not chat:
            return Response({'error': 'Chat not found'}, status=404)
        messages = chat.messages.all()
        messages = MessageSerializer(messages, many=True).data
        username = request.user.username
        friend_username = chat.participants.exclude(user=request.user).first().user.username
        chat_pk = chat.pk
        return render(request, 'chat/room.html',
                      {'chat_pk': chat_pk, 'username': username, 'friend_username': friend_username,
                       'messages': messages})
