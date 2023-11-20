from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
   username = models.CharField(max_length=50, unique=False, null=True, blank=True)
   email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ["username"]