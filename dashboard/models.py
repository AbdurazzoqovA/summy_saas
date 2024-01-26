from django.db import models

# Create your models here.
from django.db import models
from summarizer.models import User

# Create your models here.
import uuid


# Import your Celery task


class Documents(models.Model):
    input_text = models.TextField()
    output_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    words_used = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100, null=True, blank=True)
    level = models.CharField(max_length=100, null=True, blank=True)
    readibility = models.CharField(max_length=100, null=True, blank=True)
    document_id = models.UUIDField(default=uuid.uuid4, editable=False)
    model = models.CharField(max_length=100, null=True, blank=True)
