from django.db import models


class TwitteManager(models.Manager):
    def create_twitte(self, *args, **kwargs):
        parent = kwargs.get('parent', None)
        if parent:
            kwargs['conversation'] = parent.get_conversation()
            twitte = super().create(*args, **kwargs)
        else:
            twitte = super().create(*args, **kwargs)
            twitte.conversation = twitte
            twitte.save()
        return twitte
