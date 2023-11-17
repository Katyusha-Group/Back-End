from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Value, Case, When, BooleanField, ExpressionWrapper, F, IntegerField
from django.db.models.functions import StrIndex, Lower

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Follow, Twitte
from .serializers import ProfileSerializer, UpdateProfileSerializer, FollowSerializer, FollowersYouFollowSerializer, \
    ProfileUsernameSerializer, TwitteSerializer, LikeSerializer
from utils.variables import project_variables

from .permissions import IsTwitterOwner


class ProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        token = self.get_token_for_user(self.request.user)
        return {'csrftoken': self.request.COOKIES.get('csrftoken'),
                'token': token,
                'request': self.request}

    def get_permissions(self):
        if self.action == 'delete':
            return [IsAdminUser()]
        if self.action == 'retrieve':
            return [IsAdminUser()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().exclude(content_type=ContentType.objects.get_for_model(get_user_model()),
                                               object_id=request.user.id)[0:10]
        serializer = self.get_serializer(
            queryset,
            context=self.get_serializer_context(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], serializer_class=ProfileUsernameSerializer,
            permission_classes=[IsAuthenticated], url_path='my-username')
    def my_username(self, request, *args, **kwargs):
        profile = Profile.get_profile_for_user(request.user)
        serializer = self.get_serializer(
            profile,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], serializer_class=ProfileSerializer,
            permission_classes=[IsAuthenticated], url_path='update-profile')
    def update_profile(self, request, *args, **kwargs):
        profile = Profile.get_profile_for_user(request.user)
        serializer = UpdateProfileSerializer(
            profile,
            context=self.get_serializer_context(),
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        data['image'] = f'{project_variables.DOMAIN}/{serializer.data["image"]}'
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], serializer_class=ProfileSerializer,
            url_path='(?P<username>\w+)', url_name='view-profile')
    def view_profile(self, request, username, *args, **kwargs):
        profile = Profile.objects.filter(username=username).first()
        if not profile:
            return Response({'detail': ['profile not found']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(
            profile,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='follow/(?P<username>\w+)', serializer_class=FollowSerializer, )
    def follow(self, request, username):
        follower = Profile.get_profile_for_user(request.user)
        following = FollowSerializer(data={'username': username})
        following.is_valid(raise_exception=True)
        following = following.validated_data['following']

        if follower == following:
            return Response({'detail': ['cannot follow yourself']}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=follower, following=following)

        if created:
            return Response({'detail': ['followed']}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': ['already followed']}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='unfollow/(?P<username>\w+)', serializer_class=FollowSerializer, )
    def unfollow(self, request, username):
        follower = Profile.get_profile_for_user(request.user)
        following = FollowSerializer(data={'username': username})
        following.is_valid(raise_exception=True)
        following = following.validated_data['following']

        if follower == following:
            return Response({'detail': ['cannot unfollow yourself']}, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.filter(follower=follower, following=following)

        if follow.exists():
            follow.delete()
            return Response({'detail': ['unfollowed']}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': ['not following']}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='(?P<username>\w+)/followers', serializer_class=ProfileSerializer, )
    def view_followers(self, request, username):
        profile = Profile.objects.filter(username=username).first()
        if not profile:
            return Response({'detail': ['profile not found']}, status=status.HTTP_404_NOT_FOUND)
        followers = Follow.objects.filter(following=profile).prefetch_related('follower').all()
        followers_profile = [follow.follower for follow in followers]
        serializer = self.get_serializer(
            followers_profile,
            context=self.get_serializer_context(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='(?P<username>\w+)/following', serializer_class=ProfileSerializer, )
    def view_following(self, request, username):
        profile = Profile.objects.filter(username=username).first()
        if not profile:
            return Response({'detail': ['profile not found']}, status=status.HTTP_404_NOT_FOUND)
        followings = Follow.objects.filter(follower=profile).prefetch_related('following').all()
        following_profile = [following.following for following in followings]
        serializer = self.get_serializer(
            following_profile,
            context=self.get_serializer_context(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='(?P<username>\w+)/followers-you-follow',
            serializer_class=FollowersYouFollowSerializer, )
    def view_followers_you_follow(self, request, username):
        profile = Profile.objects.filter(username=username).first()
        if not profile:
            return Response({'detail': ['profile not found']}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(
            profile,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        # This will order queryset first by users' profiles and then by other profiles. Also, if the query string
        # is found in both name or username, the queryset will be ordered by the sum of the indexes. So that the
        # profile with the query string nearer to the start of the name or username will be first.
        queryset = Profile.objects.all()
        query_string = self.request.query_params.get('search', None)
        if query_string is not None:
            content_type = ContentType.objects.get_for_model(get_user_model())
            queryset = queryset.annotate(
                username_index=StrIndex(Lower('username'), Lower(Value(query_string))),
                name_index=StrIndex(Lower('name'), Lower(Value(query_string))),
                is_user=Case(
                    When(content_type=content_type, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            ).filter(
                Q(username_index__gt=0) | Q(name_index__gt=0)
            ).annotate(
                index=ExpressionWrapper(
                    F('username_index') + F('name_index'),
                    output_field=IntegerField(),
                )
            ).order_by('-is_user', 'index').all()
        return queryset

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class TwitteViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        if self.action == 'list':
            return Twitte.objects.order_by('-created_at').filter(parent=None)
        return Twitte.objects.order_by('-created_at').all()

    def get_serializer_class(self):
        if self.action in ['like', 'unlike']:
            return LikeSerializer
        elif self.action == 'likes':
            return ProfileSerializer
        return TwitteSerializer

    def get_serializer_context(self):
        token = self.get_token_for_user(self.request.user)
        return {'csrftoken': self.request.COOKIES.get('csrftoken'),
                'token': token,
                'request': self.request}

    def get_permissions(self):
        if self.action == 'delete':
            return [IsTwitterOwner()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset(),
            context=self.get_serializer_context(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        profile = Profile.get_profile_for_user(request.user)
        serializer = self.get_serializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='(?P<pk>\d+)/likes', serializer_class=ProfileSerializer, url_name='twittes-view-likes')
    def likes(self, request, *args, **kwargs):
        twitte = self.get_object()
        serializer = self.get_serializer(
            twitte.likes.all(),
            context=self.get_serializer_context(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='(?P<pk>\d+)/children', serializer_class=TwitteSerializer, url_name='twittes-view-children')
    def children(self, request, *args, **kwargs):
        twitte = self.get_object()
        serializer = self.get_serializer(
            twitte.get_children(),
            context=self.get_serializer_context(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='(?P<pk>\d+)/like', serializer_class=LikeSerializer, )
    def like(self, request, *args, **kwargs):
        profile = Profile.get_profile_for_user(request.user)
        twitte = self.get_object()
        twitte.likes.add(profile)
        return Response({'detail': ['liked']}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='(?P<pk>\d+)/unlike', serializer_class=LikeSerializer, )
    def unlike(self, request, *args, **kwargs):
        profile = Profile.get_profile_for_user(request.user)
        twitte = self.get_object()
        twitte.likes.remove(profile)
        return Response({'detail': ['unliked']}, status=status.HTTP_200_OK)
        
    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)