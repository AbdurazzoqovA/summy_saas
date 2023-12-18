from django.contrib import admin
from . models import Subscription, WordCountTracker
# Register your models here.
admin.site.register(Subscription)
admin.site.register(WordCountTracker)