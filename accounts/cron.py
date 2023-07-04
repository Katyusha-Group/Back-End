from datetime import timedelta

from django.utils import timezone

from accounts.models import User


def reset_registration_tries():
    users = User.objects.filter(registration_tries__gt=0)
    for user in users:
        if user.last_verification_sent + timedelta(hours=12) < timezone.now():
            user.verification_tries_count = 0
            user.has_verification_tries_reset = True
            user.save()
