from django.urls import path

from .views import LoginView, RefreshView, RegisterView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', RefreshView.as_view(), name='token_refresh'),
]


