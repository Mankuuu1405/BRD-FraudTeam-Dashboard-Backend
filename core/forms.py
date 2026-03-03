from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, Role


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'phone']


class NotificationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'fraud_alert_notifications',
            'aml_screening_alerts',
            'case_status_updates'
        ]


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']


class PermissionForm(forms.Form):
    MODULES = ['cases', 'reports', 'analytics', 'settings']

    for module in MODULES:
        locals()[f"{module}_view"] = forms.BooleanField(required=False)
        locals()[f"{module}_edit"] = forms.BooleanField(required=False)
        locals()[f"{module}_create"] = forms.BooleanField(required=False)
        locals()[f"{module}_delete"] = forms.BooleanField(required=False)