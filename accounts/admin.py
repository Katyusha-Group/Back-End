from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from university.models import Department  # Import Department model


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_email_verified', 'department')
    list_filter = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'department')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'department')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_email_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'department')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
