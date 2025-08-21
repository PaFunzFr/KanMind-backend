from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    CustomUserManager that uses the EmailField as the username field (unique identifier)
    """
    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a Superuser/Admin with the given email and password
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        # create user and save to db
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User that uses the email as the username field 
    instead of the default username field.
    Email is unique identifier.
    Username is not used at all.
    """
    username = None  # delete username field out of db
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=150)
    # first_name = models.CharField(max_length=150)
    # last_name = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'  # login with email
    REQUIRED_FIELDS = ['fullname']
    # REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    # @property
    # def fullname(self):
    #     return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.fullname