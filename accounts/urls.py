from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    MeView,
    RoleChoicesView,
)

urlpatterns = [
    path('register/',        RegisterView.as_view(),       name='register'),
    path('login/',           LoginView.as_view(),          name='login'),
    path('logout/',          LogoutView.as_view(),         name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/',  ResetPasswordView.as_view(),  name='reset-password'),
    path('token/refresh/',   TokenRefreshView.as_view(),   name='token-refresh'),
    path('me/',              MeView.as_view(),              name='me'),
    path('roles/',           RoleChoicesView.as_view(),    name='role-choices'),
]