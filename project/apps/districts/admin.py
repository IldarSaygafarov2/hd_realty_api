from django.contrib import admin
from unfold.admin import ModelAdmin
from modeltranslation.admin import TranslationAdmin

from .models import District


@admin.register(District)
class DistrictAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name_ru",)}
