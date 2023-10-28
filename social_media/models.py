from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='images/profile_pics', default='images/profile_pics/default.png')

    def __str__(self):
        return self.user.email

