from django.urls import path, include
from .views import CheckCode, LogoutView, LoginView, RegisterView, PasswordResetConfirmView, PasswordRequested, RequestPasswordResetView, ConfirmEmail, signup_redirect
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-requested/', PasswordRequested.as_view(), name='password_requested'),
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request_password_reset'),
    path('confirm-email/', ConfirmEmail.as_view(), name='confirm_email'),
    path('check-code/', CheckCode.as_view(), name='check_code'),    
    path('social/signup/', signup_redirect, name='signup_redirect'),
]