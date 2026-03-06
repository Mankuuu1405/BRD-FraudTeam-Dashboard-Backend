from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import NotificationPreference, Role, UserRole, Module, Permission


UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = UserModel
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'username', 'role', 'groups_list']
    
    role = serializers.CharField(read_only=True)
    groups_list = serializers.SerializerMethodField()

    def get_groups_list(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_fields(self):
        fields = super().get_fields()
        model_field_names = {field.name for field in UserModel._meta.get_fields() if hasattr(field, 'name')}
        if 'phone' not in model_field_names:
            fields.pop('phone', None)
        return fields

    def update(self, instance, validated_data):
        if not hasattr(instance, 'phone'):
            validated_data.pop('phone', None)
        return super().update(instance, validated_data)


class UpdateEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if UserModel.objects.filter(email=value).exclude(pk=self.context['request'].user.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class UpdatePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data['new_password'])
        return data


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['fraud_alert_notifications', 'aml_screening_alerts', 'case_status_updates']


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name']


class PermissionSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    module_id = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(), source='module', write_only=True
    )

    class Meta:
        model = Permission
        fields = ['id', 'module', 'module_id', 'can_view', 'can_edit', 'can_create', 'can_delete']


class RoleSerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField(read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'user_count', 'permissions', 'created_at']


class RoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

    def validate_name(self, value):
        if Role.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A role with this name already exists.")
        return value


class PermissionMatrixSerializer(serializers.Serializer):
    """Used to bulk-update permissions for a role."""
    permissions = serializers.ListField(child=serializers.DictField())

    def validate_permissions(self, value):
        for item in value:
            required_keys = {'module_id', 'can_view', 'can_edit', 'can_create', 'can_delete'}
            if not required_keys.issubset(item.keys()):
                raise serializers.ValidationError(
                    f"Each permission must have: {required_keys}"
                )
        return value

class GroupSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_count']

    def get_user_count(self, obj):
        return obj.core_user_set.count()
