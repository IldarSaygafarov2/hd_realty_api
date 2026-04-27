from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import ConsultationRequest, ContactRequest


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(ModelAdmin):
    list_display = ("name", "phone", "goal", "status", "created_at")
    list_filter = ("status", "goal", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "phone")
    readonly_fields = ("name", "phone", "goal", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Заявка",
            {
                "fields": ("name", "phone", "goal"),
            },
        ),
        (
            "Обработка",
            {
                "fields": ("status", "comment"),
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

    def has_add_permission(self, request):
        return False


@admin.register(ContactRequest)
class ContactRequestAdmin(ModelAdmin):
    list_display = ("name", "phone", "status", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "phone")
    readonly_fields = ("name", "phone", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Заявка",
            {
                "fields": ("name", "phone"),
            },
        ),
        (
            "Обработка",
            {
                "fields": ("status", "comment"),
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

    def has_add_permission(self, request):
        return False
