from django.urls import path
from .views import TaskList, TaskDetail, CommentList, AssignedTasksList, ReviewTasksList, DeleteComment

urlpatterns = [
    path('', TaskList.as_view(), name='task-list'),
    path('<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('<int:pk_task>/comments/', CommentList.as_view(), name='comment-list'),
    path('assigned-to-me/', AssignedTasksList.as_view(), name='assigned-tasks'),
    path('reviewing/', ReviewTasksList.as_view(), name='reviewing-tasks'),
    path('<int:pk_task>/comments/<int:pk_comment>/', DeleteComment.as_view(), name='delete_comment')
]
