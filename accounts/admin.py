from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name',
                'email', 'username',
                'role',
                'password1', 'password2',
            ),
        }),
    )

    list_display   = ['username', 'email', 'full_name', 'role', 'is_staff', 'is_active', 'date_joined']
    list_filter    = ['role', 'is_staff', 'is_active']
    search_fields  = ['username', 'email', 'first_name', 'last_name']
    ordering       = ['-date_joined']
    readonly_fields = ['last_login', 'date_joined']

    def full_name(self, obj):
        return obj.get_full_name() or '—'
    full_name.short_description = 'Full Name'