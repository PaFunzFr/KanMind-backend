from rest_framework import serializers
from app_auth.models import UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email']
        extra_kwargs = {
            'username': {'required': False, 'read_only': True}, 
        }

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'repeated_password')
        extra_kwargs = {
            'password': {'write_only': True}, # password is required and write-only
            'username': {'required': False, 'read_only': True}, 
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def save(self):
        pw = self.validated_data['password']
        repeatedpw = self.validated_data['repeated_password']
        if pw != repeatedpw:
            raise serializers.ValidationError({'error': 'Passwords do not match'})
        username = f'{self.validated_data['first_name']} {self.validated_data['last_name']}'

        account = User(
            email = self.validated_data['email'],
            username=username,
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name']
        )

        account.set_password(pw)
        account.save()
        return account