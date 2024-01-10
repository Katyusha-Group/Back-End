from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from chat.models import Chat, Contact
from .serializers import ChatSerializer, CreateChatSerializer, ChatRetrieveSerializer, MessageSerializer

User = get_user_model()


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

    @action(detail=False, methods=['get'], url_path=r'chat-with/(?P<username>[\w.@+-]+)', url_name='chat-with')
    def get_chat(self, request, username):
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': 'User not found'}, status=404)
        contact = Contact.objects.get_or_create(user=user)[0]
        chat = Chat.objects.filter(participants=contact).filter(participants__user=request.user).first()
        if not chat:
            serializer = CreateChatSerializer(data={'participants': [contact.user.username]},
                                              context={'request': self.request})
            serializer.is_valid(raise_exception=True)
            chat = serializer.save()
        serializer = ChatRetrieveSerializer(chat, context={'request': self.request})
        return Response(serializer.data, status=200)

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
