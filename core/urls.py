from django.urls import path
from .views import (
    AccountProfileView,
    UpdateEmailView,
    UpdatePasswordView,
    NotificationPreferenceView,
    RoleListCreateView,
    RoleDetailDeleteView,
    PermissionMatrixView,
    ModuleListView,
)

urlpatterns = [
    # Account
    path('profile/', AccountProfileView.as_view(), name='account-profile'),
    path('email/', UpdateEmailView.as_view(), name='update-email'),
    path('password/', UpdatePasswordView.as_view(), name='update-password'),

    # Notification Preferences
    path('notifications/', NotificationPreferenceView.as_view(), name='notifications'),

    # Role Management
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleDetailDeleteView.as_view(), name='role-detail-delete'),

    # Permission Matrix
    path('roles/<int:role_id>/permissions/', PermissionMatrixView.as_view(), name='permission-matrix'),

    # Modules
    path('modules/', ModuleListView.as_view(), name='module-list'),
]