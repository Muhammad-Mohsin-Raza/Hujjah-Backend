from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from .validators import validate_saudi_phone  # 👈 import here
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, phone_number, password, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        if not email:
            raise ValueError('The Email must be set')
        if not phone_number:
            raise ValueError('The Phone number must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('role', 'user')
        return self._create_user(username, email, phone_number, password, **extra_fields)

    def create_superuser(self, username, email, phone_number, password, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(username, email, phone_number, password, **extra_fields)

    def get_by_natural_key(self, username):
        # This method is required for authentication to work properly
        return self.get(username=username)


class User(AbstractBaseUser):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        ADMIN = 'admin', 'Admin'
        ASSISTANT = 'assistant', 'Assistant'

    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15, unique=True, validators=[validate_saudi_phone])
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    username = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    parent_user = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assistants',
        help_text="If this user is an assistant, link them to their lawyer."
    )
    is_active = models.BooleanField(default=True)
    terms_accepted = models.BooleanField(
        default=False,
        help_text="Indicates whether the user has accepted the terms and conditions"
    )
    deletion_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when user requested account deletion. Account will be deleted after 30 days if no login occurs."
    )

    REQUIRED_FIELDS = ['email', 'phone_number', 'password']
    USERNAME_FIELD = 'username'
    objects = CustomUserManager()

    def __str__(self):
        return self.username
