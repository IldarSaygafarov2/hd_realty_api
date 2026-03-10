from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from .models import Advertisement, AdvertisementCharacteristic, AdvertisementImage


class AdvertisementImageInline(TabularInline, TranslationTabularInline):
    model = AdvertisementImage
    extra = 0


class AdvertisementCharacteristicInline(TabularInline, TranslationTabularInline):
    model = AdvertisementCharacteristic
    extra = 1


@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin, TranslationAdmin):
    list_display = ("title", "price", "currency", "status", "district", "created_at")
    list_filter = ("status", "category", "district")
    search_fields = ("title", "address")
    prepopulated_fields = {"slug": ("title_ru",)}
    inlines = [AdvertisementImageInline, AdvertisementCharacteristicInline]
    readonly_fields = ("views_count", "created_at", "updated_at")
