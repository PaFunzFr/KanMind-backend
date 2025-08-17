from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrMember
from app_board.models import Board
from .serializers import BoardSerializer, BoardUpdateSerializer, BoardRetrieveSerializer

class BoardList(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def perform_create(self, serializer):
        """
        set current logged user as owner
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Filter boards by current logged user,
        Does User own board or is he member of board?
        """
        user = self.request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user) 
        return owned_boards.union(member_boards) # Union of both queries, no duplicates

class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrMember]
    def get_serializer_class(self):
        """
        Chosen serializer class depends on the HTTP method.
        """
        if self.request.method in ['PATCH', 'PUT']:
            return BoardUpdateSerializer
        return BoardRetrieveSerializer # Default => GET