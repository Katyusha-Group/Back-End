from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from models import Profile
from serializers import ProfileSerializer, UpdateProfileSerializer
from utils.variables import project_variables


class ProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'delete', 'patch', 'head', 'options']
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        token = self.get_token_for_user(self.request.user)
        return {'csrftoken': self.request.COOKIES.get('csrftoken'),
                'token': token}

    def get_permissions(self):
        if self.action == 'delete':
            return [IsAdminUser()]
        if self.action == 'retrieve':
            return [IsAdminUser()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.is_staff:
            return super().list(request, *args, **kwargs)
        profile = Profile.objects.filter(user=user).first()
        serializer = self.get_serializer(
            profile,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], serializer_class=ProfileSerializer, permission_classes=[IsAuthenticated])
    def update_profile(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        token = self.get_token_for_user(user)
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

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), user=self.request.user)

    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
