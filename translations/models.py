from django.db import models


class Language(models.Model):
    display_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.display_name


class MetaTag(models.Model):
    PAGE_CHOICES = (
        ("main", "Main"),
        ("pricing", "Pricing"),
        ("sign_up", "Sign Up"),
        ("sign_in", "Sign In"),
        ("log_out", "Log Out"),
        ("confirm_page", "Confirm Page"),
        ("forgot_password", "Forgot Password"),
        # Add more pages as needed
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    page_identifier = models.CharField(max_length=100, choices=PAGE_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to="og_images/", blank=True, null=True)
    twitter_title = models.CharField(max_length=200, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.ImageField(
        upload_to="twitter_images/", blank=True, null=True
    )

    def __str__(self):
        return f"{self.page_identifier} ({self.language.display_name})"
