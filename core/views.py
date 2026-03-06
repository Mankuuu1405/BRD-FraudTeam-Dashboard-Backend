from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

UserModel = get_user_model()
from .models import NotificationPreference, Role, Module, Permission
from core.serializers import (
    UserSerializer,
    UpdateEmailSerializer,
    UpdatePasswordSerializer,
    NotificationPreferenceSerializer,
    RoleSerializer,
    RoleCreateSerializer,
    PermissionSerializer,
    PermissionMatrixSerializer,
    GroupSerializer
)
# ─── Account ────────────────────────────────────────────────────────────────

class AccountProfileView(generics.RetrieveUpdateAPIView):
    """GET / PATCH  /api/settings/profile/"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateEmailView(APIView):
    """PATCH  /api/settings/email/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateEmailSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.email = serializer.validated_data['email']
        request.user.save()
        return Response({'detail': 'Email updated successfully.'})


class UpdatePasswordView(APIView):
    """PATCH  /api/settings/password/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password updated successfully.'})


# ─── Notification Preferences ────────────────────────────────────────────────

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """GET / PATCH  /api/settings/notifications/"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj


# ─── Role Management ─────────────────────────────────────────────────────────

class RoleListCreateView(generics.ListCreateAPIView):
    """GET /api/settings/roles/  →  list all roles with user count
       POST /api/settings/roles/  →  create new role"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Role.objects.prefetch_related('permissions__module').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleCreateSerializer
        return RoleSerializer


class RoleDetailDeleteView(generics.RetrieveDestroyAPIView):
    """GET  /api/settings/roles/<id>/
       DELETE  /api/settings/roles/<id>/"""
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()


# ─── Permission Matrix ────────────────────────────────────────────────────────

class PermissionMatrixView(APIView):
    """GET  /api/settings/roles/<role_id>/permissions/
       POST /api/settings/roles/<role_id>/permissions/  →  bulk save"""
    permission_classes = [IsAuthenticated]

    def get(self, request, role_id):
        role = get_object_or_404(Role, pk=role_id)
        modules = Module.objects.all()
        permissions = Permission.objects.filter(role=role).select_related('module')
        perm_map = {p.module_id: p for p in permissions}

        data = []
        for module in modules:
            perm = perm_map.get(module.id)
            data.append({
                'module': {'id': module.id, 'name': module.name},
                'can_view': perm.can_view if perm else False,
                'can_edit': perm.can_edit if perm else False,
                'can_create': perm.can_create if perm else False,
                'can_delete': perm.can_delete if perm else False,
            })
        return Response({'role': role.name, 'permissions': data})

    def post(self, request, role_id):
        role = get_object_or_404(Role, pk=role_id)
        serializer = PermissionMatrixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for item in serializer.validated_data['permissions']:
            module = get_object_or_404(Module, pk=item['module_id'])
            Permission.objects.update_or_create(
                role=role,
                module=module,
                defaults={
                    'can_view': item['can_view'],
                    'can_edit': item['can_edit'],
                    'can_create': item['can_create'],
                    'can_delete': item['can_delete'],
                }
            )
        return Response({'detail': 'Permissions saved successfully.'})


# ─── Teams / Users ────────────────────────────────────────────────────────────

class UserListView(generics.ListAPIView):
    """GET /api/settings/users/"""
    queryset = UserModel.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class GroupListView(generics.ListAPIView):
    """GET /api/settings/groups/"""
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

class ModuleListView(generics.ListAPIView):
    """GET  /api/settings/modules/"""
    queryset = Module.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        from .serializers import ModuleSerializer
        serializer = ModuleSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)