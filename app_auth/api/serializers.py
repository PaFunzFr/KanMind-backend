"""
Serializers for user registration, authentication, and user info.

This module provides:
- Hyperlinked representation of users for REST navigation.
- Compact user detail/info serializers for read operations.
- A registration serializer with email uniqueness and password confirmation.
- A login serializer that authenticates users using Django's auth system.

Conventions:
- DRF-compatible docstrings and field metadata (write_only).
- Validation errors use DRF's serializers.ValidationError with clear messages.
- Passwords are never returned; only write-only handling is used.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Hyperlinked representation of a user for list/detail endpoints.

    Purpose:
        Expose a navigable URL along with basic user-identifying fields.

    Fields:
        url (HyperlinkedIdentity): Canonical URL of this user resource.
        fullname (str): User’s display name.
        email (Email): User’s unique email address.

    Notes:
        - Requires a DefaultRouter or proper view_name configuration so that
          the hyperlinked 'url' can be resolved.
    """
    class Meta:
        model = User 
        fields = ['url', 'fullname', 'email']

class UserDetailSerializer(serializers.ModelSerializer):
    """
    Read-only details of a single user.

    Fields:
        id (int): Primary key.
        fullname (str): User’s display name.
        email (Email): User’s email address.

    Notes:
        - If using a custom user model and custom router name, ensure the
          detail route name matches (e.g., 'customuser-detail').
    """
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']

class UserInfoSerializer(serializers.ModelSerializer):
    """
    Compact user info serializer for embedding in other payloads.

    Fields:
        id (int): Primary key.
        fullname (str): User’s display name.
        email (Email): User’s email address.

    Typical uses:
        - Nested representations (e.g., owners, assignees).
        - Lightweight projections for list endpoints.
    """
    class Meta:
        model = User 
        fields = ['id', 'fullname', 'email']

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Handles user sign-up with email uniqueness and password confirmation.

    Input:
        fullname (str, write-only): User’s display name.
        email (Email, write-only): Must be unique.
        password (str, write-only): Plain password; hashed via set_password().
        repeated_password (str, write-only): Must match 'password'.

    Output:
        User instance (without exposing password).

    Validation:
        - validate_email: Fails if the email is already in use.
        - save: Ensures 'password' == 'repeated_password'.

    Errors:
        - {"email": ["Email already exists"]} when duplicate email.
        - {"error": "Passwords do not match"} when confirmation fails.

    Security:
        - Passwords are never returned.
        - Uses Django’s password hashing via set_password().
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}, # password write-only
            'fullname': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def save(self):
        pw = self.validated_data['password']
        repeatedpw = self.validated_data['repeated_password']
        if pw != repeatedpw:
            raise serializers.ValidationError({'error': 'Passwords do not match'})

        account = User(
            email = self.validated_data['email'],
            fullname = self.validated_data['fullname'],
        )

        account.set_password(pw)
        account.save()
        return account
    
class LoginSerializer(serializers.Serializer):
    """
    Validate user credentials and attach the authenticated user.

    Input:
        email (Email): User’s email used for login.
        password (str, write-only): Plain password.

    Output:
        data with 'user' key set to the authenticated user instance.

    Behavior:
        - Uses Django's authenticate(), which handles proper password hashing.
        - Rejects inactive accounts.

    Errors:
        - "Must include email and password" if required fields are missing.
        - "Invalid email or password" if authentication fails.
        - "User account is disabled" if user.is_active is False.

    Notes:
        - Assumes AUTHENTICATION_BACKENDS support email-as-username or that
          the email is mapped to the 'username' parameter in authenticate().
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            
            data['user'] = user  # Authenticated user
            return data
        else:
            raise serializers.ValidationError("Must include email and password")