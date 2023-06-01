from django.db import models
from django.db.models.signals import post_save
from django_jalali.db import models as jmodels


class SignalSenderManager(models.Manager):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        result = super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
        print(f'{objs[0].__class__.__name__} --- {len(objs)} objects created')
        return result

    def bulk_update(self, objs, fields, batch_size=None):
        result = super().bulk_update(objs, fields, batch_size=len(objs))
        print(f'{objs[0].__class__.__name__} --- {len(objs)} objects updated')
        return result


class jSignalSenderManager(jmodels.jManager):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        result = super().bulk_create(objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts)
        print(f'{objs[0].__class__.__name__} --- {len(objs)} objects created')
        return result
