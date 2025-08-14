from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User 
        fields = ['url', 'fullname', 'email']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User # used Model (overwritten) => CustomUser => path(.... name='customuser-detail') not user-detail
        fields = ['id', 'first_name', 'last_name', 'email']

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'fullname', 'email']

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}, # password write-only
            'first_name': {'write_only': True},
            'last_name': {'write_only': True},
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
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name']
        )

        account.set_password(pw)
        account.save()
        return account
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            # Django's authenticate() uses correct password-hashing
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            
            data['user'] = user  # Authenticated user
            return data
        else:
            raise serializers.ValidationError("Must include email and password")