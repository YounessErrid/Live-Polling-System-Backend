from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # username = None  # Remove the username field
    email = models.EmailField(_('email address'), unique=True)  # Make email unique and required

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    objects = CustomUserManager()  # Use the custom user manager

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = []  # No additional required fields
    

    def __str__(self):
        return self.email


# Poll Model
class Poll(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="polls")
    question = models.CharField(max_length=300)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Fixed to auto update

    def __str__(self):
        return self.question

# Choice Model
class Choice(models.Model):
    choice_text = models.CharField(max_length=300)
    voters = models.ManyToManyField(CustomUser, related_name="voted_choices", blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="choices")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Fixed to auto update

    def vote_count(self):
        return self.voters.count()  # Returns number of votes for this choice

    def __str__(self):
        return self.choice_text