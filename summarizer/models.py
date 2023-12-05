from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.urls import reverse

class User(AbstractUser):
   username = models.CharField(max_length=50, unique=False, null=True, blank=True)
   email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ["username"]
   
class Blog(models.Model):
   title = models.CharField(max_length=55)
   description = RichTextField(blank=True, null=True)
   date = models.DateTimeField(auto_now_add=True)
   image = models.ImageField(upload_to='static/front/images/blog/', null=True, blank=True)
   slug = models.SlugField(null=True, blank=True)
   
   def __str__(self):
      return self.title

   def get_absolute_url(self):
      return reverse("article_detail", kwargs={"slug": self.slug})