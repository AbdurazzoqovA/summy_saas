from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.utils import timezone

from allauth.socialaccount.models import SocialAccount
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from django.db.models.signals import post_save

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


class SummaryRequestCounter(models.Model):
    ip_address = models.CharField(max_length=45)
    words_count = models.IntegerField(default=0)
    last_request_time = models.DateTimeField(auto_now=True)


@receiver(email_confirmed)
def activate_user(sender, request, email_address, **kwargs):

   from payments.models import Subscription, WordCountTracker

   """Activate user once the email address is confirmed."""
   user = email_address.user
   user.is_active = True
   user.save()
   subscriopton,created = Subscription.objects.get_or_create(
            user_id=user.id,
            plan_type="free",
            word_count=1200,
            price_in_cents=0,
            start_date=timezone.now(),
            is_active=True,
        )
   word_counter = WordCountTracker.objects.get_or_create(
      subscription_id=subscriopton.id, words_purchased=1200, words_used=0
   )

# SocialAccount.objects.filter(user=user).exists()


@receiver(post_save, sender=SocialAccount)
def activate_user_social(sender, instance, created, **kwargs):
    from payments.models import Subscription, WordCountTracker

    if created:
        user = instance.user
        user.is_active = True
        user.save()
        subscriopton = Subscription.objects.create(
            user_id=user.id,
            plan_type="free",
            word_count=1200,
            price_in_cents=0,
            start_date=timezone.now(),
            is_active=True,
        )
        word_counter = WordCountTracker.objects.create(
            subscription_id=subscriopton.id, words_purchased=1200, words_used=0
        )
