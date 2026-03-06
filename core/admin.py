
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, NotificationPreference, Role, UserRole, Module, Permission

# ─────────────────────────────────────────────────────────────
# FIXED MODULES
# ─────────────────────────────────────────────────────────────

FIXED_MODULES = ['Cases', 'Reports', 'Analytics', 'Settings']


def seed_fixed_modules():
    modules = []
    for name in FIXED_MODULES:
        module, _ = Module.objects.get_or_create(name=name)
        modules.append(module)
    return modules


def seed_role_permissions(role):
    modules = seed_fixed_modules()

    for module in modules:
        Permission.objects.get_or_create(
            role=role,
            module=module
        )


# ─────────────────────────────────────────────────────────────
# Permission Inline
# ─────────────────────────────────────────────────────────────

class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 0
    fields = ['module', 'can_view', 'can_edit', 'can_create', 'can_delete']
    show_change_link = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            module__name__in=FIXED_MODULES
        ).select_related('module')


# ─────────────────────────────────────────────────────────────
# Role Admin (FIXED — No duplicate triggers)
# ─────────────────────────────────────────────────────────────

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_user_count', 'created_at']
    search_fields = ['name']
    inlines = [PermissionInline]

    def get_user_count(self, obj):
        return obj.user_roles.count()
    get_user_count.short_description = 'Users'


# ─────────────────────────────────────────────────────────────
# Permission Admin
# ─────────────────────────────────────────────────────────────

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'module', 'can_view', 'can_edit', 'can_create', 'can_delete']
    list_filter = ['role', 'module']
    list_editable = ['can_view', 'can_edit', 'can_create', 'can_delete']
    ordering = ['role__name', 'module__name']


# ─────────────────────────────────────────────────────────────
# Module Admin
# ─────────────────────────────────────────────────────────────

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


# ─────────────────────────────────────────────────────────────
# User Admin
# ─────────────────────────────────────────────────────────────

class NotificationPreferenceInline(admin.StackedInline):
    model = NotificationPreference
    can_delete = False
    extra = 0
    fields = [
        'fraud_alert_notifications',
        'aml_screening_alerts',
        'case_status_updates'
    ]


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1
    fk_name = 'user'
    readonly_fields = ['assigned_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )

    list_display = ['username', 'email', 'first_name', 'last_name', 'phone', 'get_roles', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    ordering = ['username']
    readonly_fields = ['last_login', 'date_joined']
    inlines = [UserRoleInline]

    def get_roles(self, obj):
        roles = [ur.role.name for ur in obj.user_roles.select_related('role').all()]
        return ', '.join(roles) if roles else '—'
    get_roles.short_description = 'Roles'