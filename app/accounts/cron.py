import time
from datetime import timedelta

from django.utils import timezone

from accounts.models import User


def reset_verification_tries():
    pre = time.time()

    users = User.objects.filter(verification_tries_count__gt=0)
    for user in users:
        if user.last_verification_sent + timedelta(hours=12) < timezone.now():
            user.verification_tries_count = 0
            user.has_verification_tries_reset = True
            user.save()

    print(str(users.count()) + " users' reset verification tries have been reset.")
    print('reset_verification_tries took: ', str(time.time() - pre))
