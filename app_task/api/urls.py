"""
URL configuration for task and comment endpoints.

Provides RESTful routes for:
- Listing and creating tasks.
- Retrieving, updating, and deleting a single task.
- Listing/creating comments for a task.
- Listing tasks assigned to the current user.
- Listing tasks the current user is reviewing.
- Deleting a specific comment of a task.

Named routes:
- 'task-list'          -> collection endpoint for tasks (list/create)
- 'task-detail'        -> single-task endpoint (retrieve/update/partial_update/destroy)
- 'comment-list'       -> comments collection for a task (list/create)
- 'assigned-tasks'     -> tasks assigned to the authenticated user (list)
- 'reviewing-tasks'    -> tasks where the authenticated user is reviewer (list)
- 'delete_comment'     -> delete a specific comment of a task
"""
from django.urls import path
from .views import TaskList, TaskDetail, CommentList, AssignedTasksList, ReviewTasksList, DeleteComment

urlpatterns = [
    # GET  /tasks/           -> List tasks
    # POST /tasks/           -> Create a task
    path('', TaskList.as_view(), name='task-list'),

    # GET    /tasks/<pk>/    -> Retrieve a task
    # PUT    /tasks/<pk>/    -> Update a task (full)
    # PATCH  /tasks/<pk>/    -> Update a task (partial)
    # DELETE /tasks/<pk>/    -> Delete a task
    path('<int:pk>/', TaskDetail.as_view(), name='task-detail'),

    # GET  /tasks/<pk_task>/comments/ -> List comments for a task
    # POST /tasks/<pk_task>/comments/ -> Create a new comment for the task
    path('<int:pk_task>/comments/', CommentList.as_view(), name='comment-list'),

    # GET /tasks/assigned-to-me/ -> List tasks assigned to the current user
    path('assigned-to-me/', AssignedTasksList.as_view(), name='assigned-tasks'),

    # GET /tasks/reviewing/ -> List tasks where the current user is the reviewer
    path('reviewing/', ReviewTasksList.as_view(), name='reviewing-tasks'),

    # DELETE /tasks/<pk_task>/comments/<pk_comment>/ -> Delete a specific comment
    path('<int:pk_task>/comments/<int:pk_comment>/', DeleteComment.as_view(), name='delete_comment')
]
