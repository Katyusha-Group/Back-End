from django.db import models


class ChatQuerySet(models.QuerySet):
    def get_20_last_messages(self, chat_id):
        chat = self.get(id=chat_id)
        return chat.messages.order_by('-time_created').all()[:20]


class MessageQuerySet(models.QuerySet):
    def read(self):
        return self.filter(is_read=True)

    def unread(self):
        return self.filter(is_read=False)

    def mark_all_as_read(self):
        return self.update(is_read=True)

    def mark_all_as_unread(self):
        return self.update(is_read=False)

    def mark_as_read(self, message_id):
        return self.filter(id=message_id).update(is_read=True)

    def mark_as_unread(self, message_id):
        return self.filter(id=message_id).update(is_read=False)
