"""
URL configuration for user-related endpoints.

Exposes RESTful routes for:
- Listing and retrieving user profiles.
- Registering a new user account.
- Logging in with email/password credentials.
- Checking whether an email is already in use.

Conventions:
- Uses class-based views for list/detail, registration, and login.
- Names are provided where reverse URL resolution is required (e.g., 'customuser-detail').
- The custom user model is exposed under 'customuser-detail' to reflect an overridden User model.

Example usage (reverse):
    reverse('customuser-detail', kwargs={'pk': 1})
    reverse('registration')
    reverse('login')
    reverse('email_check')
"""

from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegistrationView, LoginView, email_check

urlpatterns = [
    path('users/', UserProfileList.as_view()),
    # used Model (overwritten) => CustomUser => path(.... name='customuser-detail') not user-detail:
    path('users/<int:pk>/', UserProfileDetail.as_view(), name='customuser-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('email-check/', email_check, name='email_check')
]