from django.db import models
from django.db.models.signals import post_save


class CourseManager(models.Manager):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        result = super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
        for i in result:
            print(i)
            post_save.send(i.__class__, instance=i, created=True)
        print(f'{objs[0].__class__} --- {len(objs)} objects created')
        return result
