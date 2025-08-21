"""
Views for user listing/detail, registration, login, and email availability checks.

Conventions:
- DRF class-based views for list/detail, registration, and login.
- Token-based authentication (rest_framework.authtoken).
- Clear permission classes per endpoint.
- Consistent 2xx/4xx status codes and structured JSON responses.

Security:
- Registration and login are open (AllowAny) but do not expose sensitive data.
- Admin-only access for retrieve/update/delete user detail.
"""

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
    """
    List users.

    GET:
        Returns a paginated list of users serialized by UserSerializer.

    Query params:
        - Standard DRF pagination/filtering (if configured globally).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user (admin-only).

    GET:
        Return details of a single user by primary key.

    PUT/PATCH:
        Update user fields. Requires admin privileges.

    DELETE:
        Delete the user. Requires admin privileges.

    Permissions:
        - IsAdminUser
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]

class RegistrationView(APIView):
    """
    Register a new user and issue an auth token.

    POST:
        Request body (JSON):
            - fullname (str, required)
            - email (str, required, unique)
            - password (str, required)
            - repeated_password (str, required; must match password)

        Responses:
            201:
                {
                    "token": "<token>",
                    "fullname": "<name>",
                    "email": "<email>",
                    "user_id": <int>
                }
            400: Validation errors (e.g., duplicate email, password mismatch)

    Permissions:
        - AllowAny
    """
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
                'user_id': saved_account.pk
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    """
    Authenticate a user and return an auth token with basic profile info.

    POST:
        Request body (JSON):
            - email (str, required)
            - password (str, required)

        Responses:
            200:
                {
                    "token": "<token>",
                    "fullname": "<name>",
                    "email": "<email>",
                    "user_id": <int>
                }
            400: Validation error (missing fields, invalid credentials, disabled account)

    Notes:
        - Uses LoginSerializer to validate credentials.
        - Token is created on first login or reused thereafter.
    """
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
    """
    Check whether an email exists in the database.

    GET:
        Query params:
            - email (str, required): Email address to check.

        Responses:
            200 (exists):
                {
                    "id": <int>,
                    "email": "<email>",
                    "fullname": "<name>"
                }
            400 (missing email):
                {"error": "Email required"}
            404 (not found):
                {"error": "Email not found"}

    Notes:
        - Lightweight function-based endpoint for quick availability checks.
    """
    email = request.query_params.get('email') # get email from request in url
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