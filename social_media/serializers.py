from rest_framework import serializers
from models import Profile
from utils.telegram.telegram_functions import get_bot_url
from utils.variables import project_variables


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email', read_only=True)
    department = serializers.CharField(source='user.department', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    telegram_link = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)

    def get_image(self, obj: Profile):
        return project_variables.DOMAIN + obj.image.url \
            if obj.image \
            else project_variables.DOMAIN + '/media/profile_pics/default.png'

    def get_telegram_link(self, obj: Profile):
        return get_bot_url(csrftoken=self.context['csrftoken'],
                           token=self.context['token'])

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'department', 'gender', 'image', 'telegram_link']


class UpdateProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.CharField(source='user.email', read_only=True)
    department = serializers.CharField(source='user.department', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    telegram_link = serializers.SerializerMethodField(read_only=True)

    def get_telegram_link(self, obj: Profile):
        return get_bot_url(csrftoken=self.context['csrftoken'],
                           token=self.context['token'])

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'user':
                user = instance.user
                fields = []
                for user_field, user_value in value.items():
                    setattr(user, user_field, user_value)
                    fields += [user_field]
                user.save()
            else:
                setattr(instance, field, value)
        instance.save()
        return instance

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'department', 'gender', 'image', 'telegram_link']

