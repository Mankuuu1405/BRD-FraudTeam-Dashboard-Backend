from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('REVIEWER',    'Reviewer'),
        ('UNDERWRITER', 'Underwriter'),
        ('ANALYST',     'Analyst'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='REVIEWER'
    )

    # Fix: unique related_names to avoid clash with core.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='accounts_user_set',
        related_query_name='accounts_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='accounts_user_set',
        related_query_name='accounts_user',
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'