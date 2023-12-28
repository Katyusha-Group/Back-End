from rest_framework import serializers

from chat.models import Chat, Contact, Message
from chat.scripts.chat_views import get_or_create_user_contact


class ContactSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class MessageSerializer(serializers.ModelSerializer):
    author = ContactSerializer()
    delta_time = serializers.SerializerMethodField()

    def get_delta_time(self, obj):
        return obj.delta_time

    class Meta:
        model = Message
        fields = ['author', 'content', 'created_at', 'delta_time']
        read_only = ['author', 'content', 'created_at', 'delta_time']


class ChatRetrieveSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)
    messages = serializers.SerializerMethodField()

    def get_messages(self, obj):
        messages_data = MessageSerializer(obj.messages.all(), many=True).data
        return messages_data

    class Meta:
        model = Chat
        fields = ['id', 'messages', 'participants']
        read_only = ['id', 'messages', 'participants']


class ChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)
    top_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    def get_top_message(self, obj):
        if obj.messages.count() == 0:
            return None
        return MessageSerializer(obj.messages.order_by('-created_at')[0]).data

    def get_unread_count(self, obj):
        return obj.messages.unread().count()

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'top_message', 'unread_count']
        read_only = ['id', 'participants', 'top_message', 'unread_count']


class CreateChatSerializer(serializers.ModelSerializer):
    participants = ContactSerializer(many=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants']
        read_only = ['id', ]

    def validate_participants(self, value):
        # Only accepting one participant for now
        if len(value) != 1:
            raise serializers.ValidationError('Participants must be more than one')
        if not isinstance(value, list):
            raise serializers.ValidationError('Participants must be a list')
        for username in value:
            if username == self.context['request'].user.username:
                raise serializers.ValidationError('User cannot create chat with himself')
        return value

    def create(self, validated_data):
        username = self.context['request'].user.username
        participants = validated_data.pop('participants')
        participants.append(username)
        chat = Chat()
        chat.save()
        for username in participants:
            contact = get_or_create_user_contact(username)
            chat.participants.add(contact)
        chat.save()
        return chat
