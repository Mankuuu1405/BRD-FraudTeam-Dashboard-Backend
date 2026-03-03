"""
URL configuration for fraud_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # JWT Auth
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Core App (Settings)
    path('api/settings/', include('core.urls')),

    # Cases App
    path('api/cases/', include('cases.urls')),

    # Reports App
    path('api/reports/', include('reports.urls')),

    # Dashboard App
    path('dashboard/', include('dashboard.urls')),
    path("api/", include("accounts.urls")),
    path('admin/', admin.site.urls),

    # Accounts — Sign In / Sign Up / Forgot Password
    path('api/accounts/', include('accounts.urls')),

    # Core — Settings (profile, roles, permissions, notifications)
    path('api/', include('core.urls')),

    # Cases
    path('api/cases/', include('cases.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


