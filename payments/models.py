from django.db import models
from django.utils import timezone
from summarizer.models import User


# Create your models here.
class Subscription(models.Model):
    # Subscription Plan Choices
    MONTHLY = "monthly"
    YEARLY = "yearly"

    FREE = "free"

    PLAN_CHOICES = [
        (MONTHLY, "Monthly"),
        (YEARLY, "Yearly"),
        (FREE, "Free"),
    ]

    # Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES)
    word_count = models.PositiveIntegerField()
    price_in_cents = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(
        null=True, blank=True
    )  # For fixed duration subscriptions
    actual_end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(
        max_length=100, blank=True, null=True
    )  # To store the Stripe subscription ID

    # Optional fields based on your requirement
    # For example, you might want to store discount information for yearly plans
    discount_applied = models.BooleanField(default=False)
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.plan_type}"


class WordCountTracker(models.Model):
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE)
    words_purchased = models.PositiveIntegerField()
    words_used = models.PositiveIntegerField(default=0)

    @property
    def words_remaining(self):
        return self.words_purchased - self.words_used

    def update_words_used(self, words):
        """
        Update the word count after a user uses some words.
        """
        self.words_used += words
        self.save()

    @property
    def is_near_limit(self):
        threshold = 0.1  # or any other percentage you deem appropriate
        return self.words_remaining <= self.words_purchased * threshold

    def __str__(self):
        return (
            f"{self.subscription.user.email} - Words Remaining: {self.words_remaining}"
        )
