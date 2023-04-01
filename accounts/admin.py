from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'is_staff', 'is_active', 'is_email_verified' )
    list_filter = ('email', 'username', 'first_name',
                   'last_name', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', )}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_email_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)
    



