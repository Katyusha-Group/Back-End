from rest_framework import serializers

from accounts.models import User
from .models import Profile
from utils.variables import project_variables


class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)
    department = serializers.CharField()

    # telegram_link = serializers.SerializerMethodField(read_only=True)

    # def get_telegram_link(self, obj: Profile):
    #     return get_bot_url(csrftoken=self.context['csrftoken'],
    #                        token=self.context['token'])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'department']


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    profile_type = serializers.CharField(read_only=True)

    def get_image(self, obj: Profile):
        return project_variables.DOMAIN + obj.image.url \
            if obj.image \
            else project_variables.DOMAIN + '/media/profile_pics/default.png'

    class Meta:
        model = Profile
        fields = ['name', 'username', 'image', 'profile_type']


class UpdateProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    profile_type = serializers.CharField(read_only=True)

    content_object = serializers.SerializerMethodField()

    def get_content_object(self, obj):
        content_object = obj.content_object
        # Determine the model type and return the appropriate serializer
        if isinstance(content_object, User):
            serializer = UserProfileSerializer(content_object, context=self.context)
            return serializer.data
        else:
            return None

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'content_object':
                user = instance.user
                for user_field, user_value in value.items():
                    setattr(user, user_field, user_value)
                user.save()
            else:
                setattr(instance, field, value)
        instance.save()
        return instance

    class Meta:
        model = Profile
        fields = ['name', 'username', 'image', 'profile_type', 'content_object']

