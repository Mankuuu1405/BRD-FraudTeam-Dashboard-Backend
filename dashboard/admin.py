# from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Applicant, Alert

# from django.contrib import admin
# from .models import Role

# @admin.register(Role)
# class RoleAdmin(admin.ModelAdmin):
#     list_display = ('name', 'created_at')  # columns shown in list view
#     search_fields = ('name',)              # add search box for role names
#     ordering = ('name',) 

from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from .models import User

class UserAdminForm(forms.ModelForm):
    full_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill full_name from first + last
        if self.instance.pk:
            self.fields['full_name'].initial = (
                f"{self.instance.first_name} {self.instance.last_name}".strip()
            )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user_id = self.instance.pk

        if User.objects.filter(email=email).exclude(pk=user_id).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        # Split full name
        full_name = self.cleaned_data.get("full_name")
        if full_name:
            parts = full_name.strip().split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        if commit:
            user.save()

        return user


# -----------------------------
# Custom User Admin
# -----------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminForm

    list_display = ("username", "email", "first_name", "last_name", "is_staff")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("full_name", "email", "phone")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

admin.site.register(Applicant)
admin.site.register(Alert)