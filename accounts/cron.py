from datetime import timedelta

from django.utils import timezone

from accounts.models import User


def reset_registration_tries():
    users = User.objects.filter(registration_tries__gt=0)
    for user in users:
        if user.last_registration_sent + timedelta(hours=12) < timezone.now():
            user.registration_tries = 0
            user.has_registration_tries_reset = True
            user.save()


def reset_verification_tries():
    users = User.objects.filter(count_of_verification_code_sent__gt=0)
    for user in users:
        if user.last_verification_sent + timedelta(hours=12) < timezone.now():
            user.count_of_verification_code_sent = 0
            user.save()
