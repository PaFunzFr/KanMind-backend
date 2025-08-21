"""
URL configuration for board endpoints.

Provides RESTful routes for:
- Listing and creating boards.
- Retrieving, updating, and deleting a single board by primary key.

Names:
- 'board-list'   -> collection endpoint (list/create)
- 'board-detail' -> single-resource endpoint (retrieve/update/partial_update/destroy)

Example reverse usage:
    reverse('board-list')
    reverse('board-detail', kwargs={'pk': 42})
"""
from django.urls import path
from .views import BoardList, BoardDetail

urlpatterns = [
    # GET  /boards/        -> List boards
    # POST /boards/        -> Create a new board
    path('', BoardList.as_view(), name='board-list'),

    # GET    /boards/<pk>/ -> Retrieve a board
    # PUT    /boards/<pk>/ -> Update a board (full)
    # PATCH  /boards/<pk>/ -> Update a board (partial)
    # DELETE /boards/<pk>/ -> Delete a board
    path('<int:pk>/', BoardDetail.as_view(), name="board-detail") 
]
