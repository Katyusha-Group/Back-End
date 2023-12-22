from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from chat.models import Chat, Contact
from chat.scripts.chat_views import get_or_create_user_contact
from .serializers import ChatSerializer

User = get_user_model()


# TODO: Add contacts viewset later


class ChatViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Chat.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            contact = get_or_create_user_contact(username)
            queryset = contact.chats.all()
        # TODO: Check the next line's logic
        return queryset
