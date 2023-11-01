from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, Follow
from .pagination import DefaultPagination
from .serializers import ProfileSerializer, UpdateProfileSerializer, FollowSerializer, SimpleProfileSerializer
from utils.variables import project_variables


class ProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

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

    @action(detail=False, methods=['get'], serializer_class=ProfileSerializer,
            permission_classes=[IsAuthenticated], url_path='me')
    def my_profile(self, request, *args, **kwargs):
        profile = Profile.get_profile_for_user(request.user)
        serializer = self.get_serializer(
            profile,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], serializer_class=ProfileSerializer,
            url_path='(?P<username>\w+)', url_name='view-profile')
    def view_profile(self, request, username, *args, **kwargs):
        profile = Profile.objects.filter(username=username).first()
        serializer = self.get_serializer(
            profile,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], serializer_class=ProfileSerializer,
            permission_classes=[IsAuthenticated], url_path='me/update')
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
        return Response(data)

    @action(detail=False, methods=['post'], url_path='follow', serializer_class=FollowSerializer, )
    def follow(self, request):
        follower = Profile.get_profile_for_user(request.user)
        following = FollowSerializer(data=request.data)
        following.is_valid(raise_exception=True)
        following = following.validated_data['following']

        if follower == following:
            return Response({'detail': 'cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(follower=follower, following=following)

        if created:
            return Response({'detail': 'followed'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'already followed'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='unfollow', serializer_class=FollowSerializer, )
    def unfollow(self, request):
        follower = Profile.get_profile_for_user(request.user)
        following = FollowSerializer(data=request.data)
        following.is_valid(raise_exception=True)
        following = following.validated_data['following']

        if follower == following:
            return Response({'detail': 'cannot unfollow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.filter(follower=follower, following=following)

        if follow.exists():
            follow.delete()
            return Response({'detail': 'unfollowed'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'not following'}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Profile.objects.order_by('content_type').all()

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
