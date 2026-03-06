
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Role(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def user_count(self):
        return self.user_roles.count()


class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    roles = models.ManyToManyField(Role, through='UserRole', related_name='users', blank=True)

    # ── Fix: add related_name to avoid clash with accounts.CustomUser ─────────
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='core_user_set',       # ← unique related_name
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='core_user_set',       # ← unique related_name
        related_query_name='core_user',
    )

    def __str__(self):
        return self.get_full_name() or self.username

    def has_module_permission(self, module_name, action):
        return Permission.objects.filter(
            role__user_roles__user=self,
            module__name=module_name,
            **{f"can_{action}": True}
        ).exists()

    @property
    def role(self):
        # Compatibility with accounts app which expects a single role string
        r = self.roles.first()
        return r.name if r else "REVIEWER"

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    def get_role_display(self):
        return self.role.capitalize()


class UserRole(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role        = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user} - {self.role}"


class NotificationPreference(models.Model):
    user                      = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    fraud_alert_notifications = models.BooleanField(default=False)
    aml_screening_alerts      = models.BooleanField(default=False)
    case_status_updates       = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification Preferences for {self.user}"


class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Permission(models.Model):
    role       = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module     = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    can_view   = models.BooleanField(default=False)
    can_edit   = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module')

    def __str__(self):
        return f"{self.role} - {self.module}"