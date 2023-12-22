from rest_framework import serializers

from chat.models import Chat, Contact
from chat.scripts.chat_views import get_or_create_user_contact


# TODO: Check this out
class ContactSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)

    class Meta:
        model = Chat
        fields = ('id', 'messages', 'participants')
        read_only = ('id')

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        chat = Chat()
        chat.save()
        for username in participants:
            contact = get_or_create_user_contact(username)
            chat.participants.add(contact)
        chat.save()
        return chat
