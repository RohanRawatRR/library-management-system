from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserRegistrationSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Public endpoint for user registration.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    """
    Wrapper around SimpleJWT's TokenObtainPairView for routing clarity.
    """


class RefreshView(TokenRefreshView):
    """
    Wrapper around SimpleJWT's TokenRefreshView for routing clarity.
    """


