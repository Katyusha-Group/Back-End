from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from .models import Chat, Room
from social_media.serializers import ProfileSerializer


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(read_only=True)

    def get_profile(self, obj):
        username = self.context['username']
        if obj.profile1.username == username:
            return ProfileSerializer(obj.profile2).data
        return ProfileSerializer(obj.profile1).data

    class Meta:
        model = Room
        fields = ['room_name', 'profile', 'date_created', 'last_updated']
