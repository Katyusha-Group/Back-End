from django.urls import reverse
from rest_framework import serializers

from accounts.models import User
from .models import Profile, Follow, Twitte, Notification
from .signals import send_notification


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


class ProfileUsernameSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ['username']


class ProfileSummarySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    profile_type = serializers.CharField(read_only=True)
    profile_link = serializers.SerializerMethodField(read_only=True)

    def get_profile_link(self, obj: Profile):
        domain = self.context['request'].META['HTTP_HOST']
        return f'http://{domain}' + reverse("profiles-view-profile", args=[obj.username])

    def get_image(self, obj: Profile):
        return obj.get_image_url(domain=self.context['request'].META['HTTP_HOST'])

    class Meta:
        model = Profile
        fields = ['name', 'username', 'image', 'profile_type', 'profile_link']


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    profile_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    is_private = serializers.BooleanField(read_only=True)
    able_to_view = serializers.SerializerMethodField(read_only=True)
    is_following_me = serializers.SerializerMethodField(read_only=True)
    is_followed = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        me = Profile.get_profile_for_user(self.context['request'].user)
        if me == instance:
            data.pop('is_following_me')
            data.pop('is_followed')
        return data

    def get_able_to_view(self, obj: Profile):
        me = Profile.get_profile_for_user(self.context['request'].user)
        if me == obj:
            return True
        if obj.is_private:
            return Follow.objects.filter(follower=me, following=obj).exists()
        return True

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
        return obj.get_image_url(domain=self.context['request'].META['HTTP_HOST'])

    class Meta:
        model = Profile
        fields = ['name', 'username', 'image', 'created_at', 'profile_type', 'is_private', 'able_to_view',
                  'is_following_me', 'is_followed', 'followers_count', 'following_count']


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
        fields = ['name', 'username', 'image', 'created_at',
                  'profile_type', 'is_private', 'content_object']


class FollowersYouFollowSerializer(serializers.ModelSerializer):
    followers_you_follow = serializers.SerializerMethodField(read_only=True)

    def get_followers_you_follow(self, obj: Profile):
        me = Profile.get_profile_for_user(self.context['request'].user)
        common_followers = (
            Follow.objects.filter(follower=me, following__in=[follow.follower for follow in
                                                              obj.followers.all().exclude(follower=me, following=obj)]))
        common_followers_profiles = [common_follower.following for common_follower in common_followers]
        return ProfileSerializer(common_followers_profiles, many=True, context=self.context).data

    class Meta:
        model = Follow
        fields = ['followers_you_follow']


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


class TwitteSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    conversation_id = serializers.SerializerMethodField(read_only=True)
    likes_count = serializers.SerializerMethodField(read_only=True)
    replies_count = serializers.SerializerMethodField(read_only=True)
    children_count = serializers.SerializerMethodField(read_only=True)
    likes_link = serializers.SerializerMethodField(read_only=True)
    children_link = serializers.SerializerMethodField(read_only=True)
    liked_by_me = serializers.SerializerMethodField(read_only=True)

    def get_likes_link(self, obj: Twitte):
        domain = self.context['request'].META['HTTP_HOST']
        return f'http://{domain}/twittes/{obj.id}/likes/'

    def get_children_link(self, obj: Twitte):
        domain = self.context['request'].META['HTTP_HOST']
        return f'http://{domain}/twittes/{obj.id}/children/'

    def get_liked_by_me(self, obj: Twitte):
        me = Profile.get_profile_for_user(self.context['request'].user)
        return obj.is_liked_by(me)

    def get_parent(self, obj: Twitte):
        return TwitteSerializer(obj.get_parent(), context=self.context).data

    def get_likes_count(self, obj: Twitte):
        return obj.get_likes_count()

    def get_replies_count(self, obj: Twitte):
        return obj.get_replies_count()

    def get_children_count(self, obj: Twitte):
        return obj.get_children_count()

    def get_conversation_id(self, obj: Twitte):
        return obj.get_conversation().id

    class Meta:
        model = Twitte
        fields = ['id', 'profile', 'content', 'created_at', 'likes_count', 'replies_count', 'children_count',
                  'likes_link', 'parent', 'children_link', 'conversation_id', 'liked_by_me']

    def create(self, validated_data):
        profile = Profile.get_profile_for_user(self.context['request'].user)
        twitte = Twitte.objects.create_twitte(profile=profile, **validated_data)
        send_notification.send(sender=Profile, notification_type=Notification.TYPE_NEW_POST,
                               actor=profile, tweet=twitte)
        return twitte

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        me = Profile.get_profile_for_user(self.context['request'].user)
        if me == instance.profile:
            data.pop('parent')
        return data


class LikeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Twitte.likes.through
        fields = ['profile']


class NotificationSerializer(serializers.ModelSerializer):
    delta_time = serializers.SerializerMethodField(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)
    tweet_link = serializers.SerializerMethodField(read_only=True)
    actor = ProfileSummarySerializer(read_only=True)
    notification_type = serializers.CharField(read_only=True)
    read = serializers.BooleanField(read_only=True)

    def get_delta_time(self, obj: Notification):
        return obj.get_delta_time()

    def get_message(self, obj: Notification):
        return obj.get_message()

    def get_tweet_link(self, obj: Notification):
        domain = self.context['request'].META['HTTP_HOST']
        return f'http://{domain}/twittes/{obj.tweet.id}/'

    class Meta:
        model = Notification
        fields = ['actor', 'notification_type', 'read', 'delta_time', 'tweet_link', 'message']
