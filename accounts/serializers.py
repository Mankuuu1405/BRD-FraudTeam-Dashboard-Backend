from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


# ── Sign Up ───────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    full_name        = serializers.CharField(write_only=True)
    password         = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ['full_name', 'email', 'role', 'password', 'confirm_password']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        validated_data.pop('confirm_password')

        # Split full name → first + last
        parts      = full_name.strip().split(' ', 1)
        first_name = parts[0]
        last_name  = parts[1] if len(parts) > 1 else ''

        # Auto-generate unique username from email
        base     = validated_data['email'].split('@')[0]
        username = base
        counter  = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        return CustomUser.objects.create_user(
            username   = username,
            email      = validated_data['email'],
            password   = validated_data['password'],
            first_name = first_name,
            last_name  = last_name,
            role       = validated_data['role'],
        )


# ── Sign In ───────────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        user = authenticate(username=user.username, password=data['password'])
        if not user:
            raise serializers.ValidationError("Incorrect password.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        data['user'] = user
        return data


# ── Forgot Password ───────────────────────────────────────────────────────────

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value


# ── Reset Password ────────────────────────────────────────────────────────────

class ResetPasswordSerializer(serializers.Serializer):
    token            = serializers.CharField()
    new_password     = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(data['new_password'])
        return data


# ── User Profile ──────────────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    full_name    = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model  = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'first_name', 'last_name', 'role', 'role_display']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username