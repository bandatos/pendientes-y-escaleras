from django.contrib import admin

from profile_auth.models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'full_editor')}),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': (
            'first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {
            'fields': ('is_superuser', 'is_staff', 'full_editor', 'is_active'),
        }),
        ('Groups', {'fields': ('groups',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # ) + UserAdmin.fieldsets
    list_display = (
        'email', 'first_name', 'last_name',
        'is_active', 'full_editor', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-is_active', 'email')
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups', 'full_editor')

