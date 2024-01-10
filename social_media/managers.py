from django.db import models
import requests


class TwitteManager(models.Manager):
    def create_twitte(self, *args, **kwargs):
        parent = kwargs.get("parent", None)
        if parent:
            kwargs["conversation"] = parent.get_conversation()
            twitte = super().create(*args, **kwargs)
        else:
            twitte = super().create(*args, **kwargs)
            twitte.conversation = twitte
            twitte.save()

        if twitte.profile.profile_type == "U" and twitte.parent is None:
            # send post request to http://37.156.144.109:7084/katyusha/twitte/ to add vector to index
            id = twitte.id
            content = twitte.content

            url = "http://37.156.144.109:7084/katyusha/twitte/"
            data = {"id": id, "text": content}
            r = requests.post(url, data=data)

        return twitte
