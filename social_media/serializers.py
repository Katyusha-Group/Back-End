from rest_framework import serializers

from accounts.models import User
from .models import Profile, Follow
from utils.variables import project_variables


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True)
    gender = serializers.CharField(read_only=True)

    # telegram_link = serializers.SerializerMethodField(read_only=True)

    # def get_telegram_link(self, obj: Profile):
    #     return get_bot_url(csrftoken=self.context['csrftoken'],
    #                        token=self.context['token'])

    class Meta:
        model = User
        fields = ['email', 'gender', 'department']


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    profile_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    description = serializers.CharField(read_only=True)
    is_following_me = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        me = Profile.get_profile_for_user(self.context['request'].user)
        if me == instance:
            data.pop('is_following')
        return data

    def get_followers_count(self, obj: Profile):
        return obj.followers.count()

    def get_following_count(self, obj: Profile):
        return obj.following.count()

    def get_is_followed(self, obj: Profile):
        me = Profile.get_profile_for_user(self.context['request'].user)
        return Follow.objects.filter(follower=me, following=obj).exists()

    def get_is_following_me(self, obj: Profile):
        me = Profile.get_profile_for_user(self.context['request'].user)
        return Follow.objects.filter(follower=obj, following=me).exists()

    def get_image(self, obj: Profile):
        return project_variables.DOMAIN + obj.image.url \
            if obj.image \
            else project_variables.DOMAIN + '/media/profile_pics/default.png'

    class Meta:
        model = Profile
        fields = ['name', 'username', 'image', 'created_at', 'profile_type', 'description', 'is_following_me',
                  'is_followed', 'followers_count', 'following_count']


class UpdateProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    profile_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

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
        fields = ['name', 'username', 'image', 'created_at', 'description', 'profile_type', 'content_object']


class FollowSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)

    def validate(self, attrs):
        attrs = super().validate(self.initial_data)

        username = attrs.get('username', None)

        if username:
            profile = Profile.objects.filter(username=username).first()

            if not profile:
                raise serializers.ValidationError({"detail": "profile does not exist."})
        else:
            raise serializers.ValidationError({"detail": "username is required."})

        return {'following': profile}


class FollowingSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['profile']
