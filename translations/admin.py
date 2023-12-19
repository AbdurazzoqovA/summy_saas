from django.contrib import admin
from .models import Language, MetaTag


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("display_name", "code")
    search_fields = ("display_name", "code")


@admin.register(MetaTag)
class MetaTagAdmin(admin.ModelAdmin):
    list_display = ("page_identifier", "language", "title")
    list_filter = ("language",)
