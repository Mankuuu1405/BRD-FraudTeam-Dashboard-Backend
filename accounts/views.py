from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import get_user_model

UserModel = get_user_model()
from .serializers import (
    RegisterSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
    UserProfileSerializer,
)


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


# ── Sign Up ───────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/accounts/register/
    {
        "full_name": "John Doe",
        "email": "john@example.com",
        "role": "REVIEWER",        ← REVIEWER / UNDERWRITER / ANALYST
        "password": "...",
        "confirm_password": "..."
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user   = serializer.save()
        tokens = get_tokens(user)
        return Response({
            'message': 'Account created successfully.',
            'tokens':  tokens,
            'user': {
                'id':       user.id,
                'email':    user.email,
                'fullName': user.get_full_name(),
                'role':     user.role,
            }
        }, status=status.HTTP_201_CREATED)


# ── Sign In ───────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    POST /api/accounts/login/
    {
        "email": "john@example.com",
        "password": "..."
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user   = serializer.validated_data['user']
        tokens = get_tokens(user)
        return Response({
            'message': 'Login successful.',
            'tokens':  tokens,
            'user': {
                'id':       user.id,
                'email':    user.email,
                'fullName': user.get_full_name(),
                'role':     user.role,
            }
        })


# ── Logout ────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    POST /api/accounts/logout/
    { "refresh": "<refresh_token>" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


# ── Forgot Password ───────────────────────────────────────────────────────────

class ForgotPasswordView(APIView):
    """
    POST /api/accounts/forgot-password/
    { "email": "john@example.com" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user  = UserModel.objects.get(email=serializer.validated_data['email'])
        uid   = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link  = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password/{uid}__{token}/"

        send_mail(
            subject        = 'Fraud Dashboard — Password Reset',
            message        = f'Reset your password:\n\n{link}',
            from_email     = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [user.email],
        )
        return Response({'message': 'Password reset link sent to your email.'})


# ── Reset Password ────────────────────────────────────────────────────────────

class ResetPasswordView(APIView):
    """
    POST /api/accounts/reset-password/
    { "token": "<uid>__<token>", "new_password": "...", "confirm_password": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid, token = serializer.validated_data['token'].split('__')
            uid  = force_str(urlsafe_base64_decode(uid))
            user = UserModel.objects.get(pk=uid)
        except Exception:
            return Response({'error': 'Invalid or expired link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired link.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password reset successfully. You can now log in.'})


# ── Me (logged in user profile) ───────────────────────────────────────────────

class MeView(APIView):
    """GET /api/accounts/me/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


# ── Role Choices (for signup dropdown) ───────────────────────────────────────

class RoleChoicesView(APIView):
    """
    GET /api/accounts/roles/
    Returns the 3 role options for the Sign Up dropdown.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response([
            {'value': 'REVIEWER',    'label': 'Reviewer'},
            {'value': 'UNDERWRITER', 'label': 'Underwriter'},
            {'value': 'ANALYST',     'label': 'Analyst'},
        ])