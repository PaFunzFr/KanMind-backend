from django.urls import path
from .views import TaskList, TaskDetail, CommentList

urlpatterns = [
    path('', TaskList.as_view(), name='task-list'),
    path('<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('<int:pk>/comments/', CommentList.as_view(), name='comment-list')
]
