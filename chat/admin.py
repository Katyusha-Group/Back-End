from django.contrib import admin

# Register your models here.

from .models import Contact, Message, Chat

admin.site.register(Contact)
admin.site.register(Message)
admin.site.register(Chat)
