from django.contrib import admin
from modeltranslation.admin import TranslationTabularInline
from unfold.admin import ModelAdmin, TabularInline

from .models import PortfolioCompletedWork, PortfolioItem, PortfolioItemImage


class PortfolioItemImageInline(TabularInline, TranslationTabularInline):
    model = PortfolioItemImage
    extra = 0
    fields = ("image",)


class PortfolioCompletedWorkInline(TabularInline, TranslationTabularInline):
    model = PortfolioCompletedWork
    extra = 0
    fields = ("title_ru", "title_uz", "icon")


@admin.register(PortfolioItem)
class PortfolioItemAdmin(ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title",)
    inlines = [PortfolioItemImageInline, PortfolioCompletedWorkInline]
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "title_ru",
                    "title_uz",
                    "description_ru",
                    "description_uz",
                    "video",
                    "is_active",
                ),
            },
        ),
        (
            "Служебное",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
