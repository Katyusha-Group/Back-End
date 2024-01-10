from django.contrib import admin


# Register your models here.
from .models import Profile, Twitte, ReportTwitte, Follow, Notification

admin.site.register(Profile)
admin.site.register(Twitte)
admin.site.register(ReportTwitte)
admin.site.register(Follow)
admin.site.register(Notification)

