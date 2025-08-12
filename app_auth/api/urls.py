from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegistrationView

urlpatterns = [
    path('users/', UserProfileList.as_view()),
    path('users/<int:pk>/', UserProfileDetail.as_view(), name='user-detail'),
    path('registration/', RegistrationView.as_view(), name='registration'),
]