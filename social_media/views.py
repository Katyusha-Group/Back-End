import requests
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Value, Case, When, BooleanField, ExpressionWrapper, F, IntegerField, Prefetch
from django.db.models.functions import StrIndex, Lower
from django.urls import reverse

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from university.models import Course, Department
from university.serializers import CourseSerializer
from .models import Profile, Follow, Twitte, Notification, ReportTwitte
from .serializers import ProfileSerializer, UpdateProfileSerializer, FollowSerializer, FollowersYouFollowSerializer, \
    ProfileUsernameSerializer, TwitteSerializer, LikeSerializer, NotificationSerializer, ReportTwitteSerializer, \
    MyProfileSerializer
from utils.variables import project_variables

from .permissions import IsTwitterOwner, IsReportTwitteOwner
from .pagination import DefaultPagination

from datetime import timedelta
from django.utils import timezone
from django.db import models


class ProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']
    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        token = self.get_token_for_user(self.request.user)
        return {'csrftoken': self.request.COOKIES.get('csrftoken'),
                'token': token,
                'request': self.request,
                'user': self.request.user}

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

    @action(detail=False, methods=['get'], serializer_class=MyProfileSerializer,
            url_path='my-profile', url_name='view-my-profile')
    def view_my_profile(self, request, *args, **kwargs):
        profile = Profile.get_profile_for_user(request.user)
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

    @action(detail=False, methods=['get'], url_path='(?P<username>\w+)/course-timeline', )
    def view_course_timeline(self, request, username: str):
        profile = Profile.objects.filter(username=username).first()
        if not profile:
            return Response({'detail': ['profile not found']}, status=status.HTTP_404_NOT_FOUND)
        if profile.profile_type != Profile.TYPE_COURSE:
            return Response({'detail': ['this timeline is for courses']}, status=status.HTTP_400_BAD_REQUEST)
        course = profile.content_object
        if not course:
            return Response({'detail': ['course not found']}, status=status.HTTP_404_NOT_FOUND)
        url = reverse('course-timeline', kwargs={'course_number': course.course_number})
        domain = self.get_serializer_context()['request'].build_absolute_uri('/')[:-1]
        headers = {
            'Authorization': f'Bearer {self.get_serializer_context()["token"]}'
        }
        response = requests.get(domain + url, headers=headers)
        return Response(response.json(), status=response.status_code)

    @action(detail=False, methods=['get'], url_path='(?P<username>\w+)/teacher-timeline', )
    def view_teacher_timeline(self, request, username: str):
        profile = Profile.objects.filter(username=username).first()
        if not profile:
            return Response({'detail': ['profile not found']}, status=status.HTTP_404_NOT_FOUND)
        if profile.profile_type != Profile.TYPE_TEACHER:
            return Response({'detail': ['this timeline is for teachers']}, status=status.HTTP_400_BAD_REQUEST)
        teacher = profile.content_object
        if not teacher:
            return Response({'detail': ['teacher not found']}, status=status.HTTP_404_NOT_FOUND)
        url = reverse('teacher-timeline', kwargs={'teacher_id': teacher.id})
        domain = self.get_serializer_context()['request'].build_absolute_uri('/')[:-1]
        headers = {
            'Authorization': f'Bearer {self.get_serializer_context()["token"]}'
        }
        response = requests.get(domain + url, headers=headers)
        return Response(response.json(), status=response.status_code)

    @action(detail=False, methods=['get'], url_path='(?P<username>\w+)/student-calendar', )
    def view_student_calendar(self, request, username: str):
        profile = Profile.objects.filter(username=username).first()
        if not profile:
            return Response({'detail': ['profile not found']}, status=status.HTTP_404_NOT_FOUND)
        if profile.profile_type != Profile.TYPE_USER and profile.profile_type != Profile.TYPE_VERIFIED_USER:
            return Response({'detail': ['this calendar is for students']}, status=status.HTTP_400_BAD_REQUEST)
        student = profile.content_object
        if not student:
            return Response({'detail': ['student not found']}, status=status.HTTP_404_NOT_FOUND)
        courses = CourseSerializer(
            (student.courses.prefetch_related('course_times',
                                              'teachers',
                                              'exam_times', )
             .select_related('base_course__department')
             .prefetch_related(Prefetch('base_course__department', Department.objects.all())).all()),
            many=True,
            context=self.get_serializer_context()
        )
        return Response(status=status.HTTP_200_OK, data=courses.data)

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
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = Twitte.objects.all()
        query_string = self.request.query_params.get('search', None)
        if query_string is not None:
            queryset = queryset.annotate(
                content_index=StrIndex(Lower('content'), Lower(Value(query_string)))
            ).filter(
                content_index__gt=0
            ).order_by('content_index').all()
        if self.action == 'list':
            return queryset.order_by('-created_at').filter(parent=None).filter(display=True)
        return queryset.order_by('-created_at').filter(display=True)

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
        if self.action == 'destroy':
            return [IsTwitterOwner()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        twitte = self.get_object()
        twitte.display = False
        twitte.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='(?P<pk>\d+)/likes', serializer_class=ProfileSerializer,
            url_name='twittes-view-likes')
    def likes(self, request, *args, **kwargs):
        twitte = self.get_object()
        serializer = self.get_serializer(
            twitte.likes.all(),
            context=self.get_serializer_context(),
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='(?P<pk>\d+)/children', serializer_class=TwitteSerializer,
            url_name='twittes-view-children')
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
        # if twitte liked by me, unlike it
        if twitte.is_liked_by(profile):
            twitte.unlike(profile)
            return Response({'detail': ['unliked']}, status=status.HTTP_204_NO_CONTENT)
        else:
            twitte.like(profile)
            return Response({'detail': ['liked']}, status=status.HTTP_201_CREATED)

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    
class FollowingTwittesViewSet(TwitteViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = Twitte.objects.all()
        query_string = self.request.query_params.get('search', None)
        if query_string is not None:
            queryset = queryset.annotate(
                content_index=StrIndex(Lower('content'), Lower(Value(query_string)))
            ).filter(
                content_index__gt=0
            ).order_by('content_index').all()
        if self.action == 'list':
            return queryset.order_by('-created_at').filter(parent=None).filter(display=True).filter(profile__in=Follow.objects.filter(
                follower=Profile.get_profile_for_user(self.request.user)).values('following'))
        return queryset.order_by('-created_at').filter(display=True).filter(profile__in=Follow.objects.filter(
            follower=Profile.get_profile_for_user(self.request.user)).values('following'))
        
        
class ForYouTwittesViewSet(TwitteViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        # i wanna get twittes that are in my followings of my followings twittes or liked by my followings
        queryset = Twitte.objects.all()
        query_string = self.request.query_params.get('search', None)
        if query_string is not None:
            queryset = queryset.annotate(
                content_index=StrIndex(Lower('content'), Lower(Value(query_string)))
            ).filter(
                content_index__gt=0
            ).order_by('content_index').all()
        if self.action == 'list':
            return queryset.filter(parent=None).filter(display=True).filter(Q(profile__in=Follow.objects.filter(
                following__in=Follow.objects.filter(
                    follower=Profile.get_profile_for_user(self.request.user)).values('following')).values('follower')) |
                Q(id__in=Twitte.objects.filter(likes__in=Follow.objects.filter(
                    follower=Profile.get_profile_for_user(self.request.user)).values('following')).values('id')))
        return queryset.order_by('-created_at').filter(display=True).filter(Q(profile__in=Follow.objects.filter(
            following__in=Follow.objects.filter(
                follower=Profile.get_profile_for_user(self.request.user)).values('following')).values('follower')) |
            Q(id__in=Twitte.objects.filter(likes__in=Follow.objects.filter(
                follower=Profile.get_profile_for_user(self.request.user)).values('following')).values('id')))
            
    
class ManageTwittesViewSet(TwitteViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        return super().get_permissions()

    def get_queryset(self):
        queryset = Twitte.objects.all()
        query_string = self.request.query_params.get('search', None)
        if query_string is not None:
            queryset = queryset.annotate(
                content_index=StrIndex(Lower('content'), Lower(Value(query_string)))
            ).filter(
                content_index__gt=0
            ).order_by('content_index').all()
        return queryset

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def get_serializer_context(self):
        token = self.get_token_for_user(self.request.user)
        return {'csrftoken': self.request.COOKIES.get('csrftoken'),
                'token': token,
                'request': self.request}

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
class ReportTwitteViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return ReportTwitte.objects.order_by('-created_at').all()

    def get_serializer_class(self):
        return ReportTwitteSerializer

    def get_serializer_context(self):
        token = self.get_token_for_user(self.request.user)
        return {'csrftoken': self.request.COOKIES.get('csrftoken'),
                'token': token,
                'request': self.request}
        
    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsReportTwitteOwner()]
        return super().get_permissions()   

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    

class ManageReportedTwittesViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        return TwitteSerializer

    def get_queryset(self):
        return Twitte.objects.filter(id__in=ReportTwitte.objects.values('twitte_id')).filter(display=True).all()

    def get_serializer_context(self):
        token = self.get_token_for_user(self.request.user)
        return {'csrftoken': self.request.COOKIES.get('csrftoken'),
                'token': token,
                'request': self.request}

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def destroy(self, request, *args, **kwargs):
        twitte = self.get_object()
        twitte.display = False
        twitte.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = Profile.get_profile_for_user(self.request.user)
        if profile.notifications.unread().exists():
            return profile.notifications.order_by('read', 'created_at').all()
        return profile.notifications.order_by('-created_at').all()

    def get_serializer_class(self):
        return NotificationSerializer

    def get_permissions(self):
        if self.action == 'unread_notifications':
            return [IsAuthenticated()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        notifications = self.get_queryset()[:5]
        serializer = self.get_serializer(
            notifications,
            many=True,
        )
        Notification.objects.filter(pk__in=[entry.pk for entry in notifications]).mark_all_as_read()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='unread-count', serializer_class=NotificationSerializer,
            url_name='unread-count')
    def unread_count(self, request, *args, **kwargs):
        user = self.request.user
        profile = Profile.get_profile_for_user(user)
        notifications = profile.notifications.unread()
        return Response({'count': notifications.count()}, status=status.HTTP_200_OK)


class TwitteChartViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAdminUser]
    queryset = Twitte.objects.all()

    def get_serializer_class(self):
        return TwitteSerializer

    @action(detail=False, methods=['get'], url_path='last-week-tweets', serializer_class=TwitteSerializer,
            url_name='last-week-tweets')
    def last_week_tweets(self, request):
        # Calculate the date a week ago from the current date
        one_week_ago = timezone.now() - timedelta(days=6)

        # Query to get the count of Tweets created per day in the last week
        tweets_per_day_last_week = Twitte.objects.filter(
            created_at__gte=one_week_ago  # Filter Tweets created after one week ago
        ).extra({
            'created_day': "date(created_at)"  # Extract day from the created_at field
        }).values('created_day').annotate(
            tweets_count_per_day=models.Count('id')  # Count Tweets per day
        ).order_by('created_day')
        
        # Create a dictionary mapping dates to the number of Tweets created that day
        tweets_per_day_last_week_dict = {}
        for entry in tweets_per_day_last_week:
            tweets_per_day_last_week_dict[entry['created_day']] = entry['tweets_count_per_day']
            
        # Create a list of dates and number of Tweets created that day
        tweets_per_day_last_week_list = []
        current_date = one_week_ago
        while current_date <= timezone.now():
            tweets_per_day_last_week_list.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'tweets_count': tweets_per_day_last_week_dict.get(current_date.date(), 0)
            })
            current_date += timedelta(days=1)
            
        # Return the response
        return Response(tweets_per_day_last_week_list, status=status.HTTP_200_OK)
