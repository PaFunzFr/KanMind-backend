from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegistrationView, LoginView

urlpatterns = [
    path('users/', UserProfileList.as_view()),
    path('users/<int:pk>/', UserProfileDetail.as_view(), name='customuser-detail'), # used Model (overwritten) => CustomUser => path(.... name='customuser-detail') not user-detail
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]