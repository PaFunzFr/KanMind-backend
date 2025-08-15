from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import UserSerializer, RegistrationSerializer, UserDetailSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

User = get_user_model()

class UserProfileList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token':token.key,
                'fullname': saved_account.fullname,
                'email':saved_account.email,
                'id': saved_account.pk
            }
        else:
            data = serializer.errors

        return Response(data)
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            # response with token and user data
            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def email_check(request):
    email = request.query_params.get('email') #get email from request in url
    if not email:
        return Response({"error": "Email required"}, status=400)
    
    try:
        user = User.objects.get(email=email)
        return Response({
            "id": user.id,
            "email": user.email,
            "fullname": user.fullname
        })
    except User.DoesNotExist:
        return Response({"error": "Email not found"}, status=404)