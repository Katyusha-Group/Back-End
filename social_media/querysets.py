from django.db import models


class NotificationQuerySet(models.QuerySet):
    def unread(self, recipient=None):
        if recipient:
            return self.filter(recipient=recipient, read=False)
        return self.filter(read=False)

    def read(self, recipient=None):
        if recipient:
            return self.filter(recipient=recipient, read=True)
        return self.filter(read=True)

    def mark_all_as_read(self, recipient=None):
        if recipient:
            return self.filter(recipient=recipient).update(read=True)
        return self.update(read=True)

    def mark_all_as_unread(self, recipient=None):
        if recipient:
            return self.filter(recipient=recipient).update(read=False)
        return self.update(read=False)
