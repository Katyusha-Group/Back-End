from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.filter(
                Q(username=username) | Q(email=username)
            ).first()
            if not user:
                raise UserModel.DoesNotExist
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
