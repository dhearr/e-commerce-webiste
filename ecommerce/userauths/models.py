from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
  email = models.EmailField(unique=True)
  username = models.CharField(max_length=150)
  bio = models.CharField(max_length=255, blank=True)
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']
  
  def __str__(self):
    return self.username
