from django.db import models


class ChatQuerySet(models.QuerySet):
    def get_20_last_messages(self, chat_id):
        chat = self.get(id=chat_id)
        return chat.messages.order_by('-time_created').all()[:20]
