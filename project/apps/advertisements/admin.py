from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from project.apps.users.utils import (
    get_moderator,
    get_realtor,
    is_moderator,
    is_realtor,
)

from .models import Advertisement, AdvertisementCharacteristic, AdvertisementImage


class AdvertisementImageInline(TabularInline, TranslationTabularInline):
    model = AdvertisementImage
    extra = 0

    def has_add_permission(self, request, obj=None):
        if is_moderator(request.user) and not request.user.is_superuser:
            return False
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_change_permission(self, request, obj=None):
        if is_moderator(request.user) and not request.user.is_superuser:
            return False
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_delete_permission(self, request, obj=None):
        if is_moderator(request.user) and not request.user.is_superuser:
            return False
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )


class AdvertisementCharacteristicInline(TabularInline, TranslationTabularInline):
    model = AdvertisementCharacteristic
    extra = 0

    def has_add_permission(self, request, obj=None):
        if is_moderator(request.user) and not request.user.is_superuser:
            return False
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_change_permission(self, request, obj=None):
        if is_moderator(request.user) and not request.user.is_superuser:
            return False
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_delete_permission(self, request, obj=None):
        if is_moderator(request.user) and not request.user.is_superuser:
            return False
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_delete_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )


@admin.register(Advertisement)
class AdvertisementAdmin(ModelAdmin, TranslationAdmin):
    list_display = (
        "title",
        "is_hot",
        "price",
        "currency",
        "status",
        "moderation_status",
        "created_by",
        "district",
        "created_at",
    )
    list_editable = ("created_by",)
    list_filter = ("status", "moderation_status", "is_hot", "category", "district")
    search_fields = ("title", "address")
    inlines = [AdvertisementImageInline, AdvertisementCharacteristicInline]
    readonly_fields = ("views_count", "created_at", "updated_at")

    fieldsets = (
        (
            "Контент объявления (для просмотра)",
            {
                "fields": (
                    "title",
                    "description",
                    "cover_image",
                    "video",
                    "address",
                    "num_rooms",
                    "area_total",
                    "area_living",
                    "floor_number",
                    "total_floors",
                    "year_built",
                    "renovation_type",
                    "price",
                    "currency",
                    "category",
                    "district",
                    "latitude",
                    "longitude",
                ),
            },
        ),
        (
            "Модерация",
            {
                "fields": ("status", "moderation_status", "created_by"),
                "description": "Укажите результат проверки объявления.",
            },
        ),
        (
            "Служебное",
            {
                "fields": ("views_count", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_prepopulated_fields(self, request, obj=None):
        # slug отсутствует в форме TranslationAdmin — отключаем prepopulate
        return {}

    def get_fieldsets(self, request, obj=None):
        if is_moderator(request.user) and not request.user.is_superuser:
            return (
                (
                    "Данные объявления (только просмотр)",
                    {
                        "fields": (
                            "title_ru",
                            "title_uz",
                            "description_ru",
                            "description_uz",
                            "cover_image",
                            "video",
                            "price",
                            "currency",
                            "address_ru",
                            "address_uz",
                            "num_rooms",
                            "area_total",
                            "area_living",
                            "floor_number",
                            "total_floors",
                            "year_built",
                            "renovation_type",
                            "category",
                            "district",
                            "latitude",
                            "longitude",
                        ),
                        "description": "Просмотрите объявление и укажите результат модерации в блоке ниже.",
                    },
                ),
                (
                    "Модерация",
                    {
                        "fields": ("status", "moderation_status", "created_by"),
                        "description": "Укажите результат проверки объявления.",
                    },
                ),
            )
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if is_moderator(request.user) and not request.user.is_superuser:
            from django import forms

            from .models import Advertisement

            class ModeratorAdvertisementForm(forms.ModelForm):
                class Meta:
                    model = Advertisement
                    fields = [
                        "title_ru",
                        "title_uz",
                        "description_ru",
                        "description_uz",
                        "address_ru",
                        "address_uz",
                        "cover_image",
                        "video",
                        "price",
                        "currency",
                        "num_rooms",
                        "area_total",
                        "area_living",
                        "floor_number",
                        "total_floors",
                        "year_built",
                        "renovation_type",
                        "category",
                        "district",
                        "latitude",
                        "longitude",
                        "status",
                        "moderation_status",
                        "created_by",
                    ]

            kwargs["form"] = ModeratorAdvertisementForm
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if is_moderator(request.user):
            moderator = get_moderator(request.user)
            realtor_ids = moderator.realtors.values_list("user_id", flat=True)
            return qs.filter(
                created_by_id__in=realtor_ids,
                moderation_status=Advertisement.ModerationStatus.PENDING,
            )
        if is_realtor(request.user):
            return qs.filter(created_by=request.user)
        return qs.none()

    def has_module_permission(self, request):
        """Показывать модуль риелторам и модераторам без проверки permissions."""
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_view_permission(self, request, obj=None):
        """Разрешить просмотр риелторам/модераторам; для объекта — только свои."""
        if request.user.is_superuser:
            return True
        if obj is None:
            return is_realtor(request.user) or is_moderator(request.user)
        if is_realtor(request.user):
            return obj.created_by_id == request.user.id
        if is_moderator(request.user):
            moderator = get_moderator(request.user)
            return obj.created_by_id in moderator.realtors.values_list(
                "user_id", flat=True
            )
        return False

    def has_add_permission(self, request):
        return request.user.is_superuser or is_realtor(request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return is_realtor(request.user) or is_moderator(request.user)
        if is_realtor(request.user):
            return obj.created_by_id == request.user.id
        if is_moderator(request.user):
            moderator = get_moderator(request.user)
            return obj.created_by_id in moderator.realtors.values_list(
                "user_id", flat=True
            )
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return is_realtor(request.user)
        if is_realtor(request.user):
            return obj.created_by_id == request.user.id
        return False

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk and is_moderator(request.user):
            try:
                old = Advertisement.objects.get(pk=obj.pk)
                old_status = old.moderation_status
            except Advertisement.DoesNotExist:
                pass

        if not change and is_realtor(request.user):
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        # Уведомление модератору при добавлении объявления риелтором
        if not change and is_realtor(request.user):
            self._create_new_ad_notification_for_moderator(obj)

        # Уведомление в админке риелтору при изменении статуса модерации
        if (
            change
            and is_moderator(request.user)
            and obj.created_by
            and old_status == Advertisement.ModerationStatus.PENDING
            and obj.moderation_status != Advertisement.ModerationStatus.PENDING
        ):
            self._create_moderation_notification(obj)

    def get_exclude(self, request, obj=None):
        exclude = list(super().get_exclude(request, obj) or [])
        if obj is None:
            exclude.extend(["created_at", "updated_at"])
        if is_realtor(request.user) and not request.user.is_superuser:
            exclude.append("created_by")
        return exclude

    def get_readonly_fields(self, request, obj=None):
        fields = ["views_count"]
        if obj:
            fields.extend(["created_at", "updated_at"])
        if is_realtor(request.user) and not request.user.is_superuser:
            fields.append("created_by")
        if is_moderator(request.user) and not request.user.is_superuser:
            fields.extend(
                [
                    "created_by",
                    "title_ru",
                    "title_uz",
                    "description_ru",
                    "description_uz",
                    "address_ru",
                    "address_uz",
                    "cover_image",
                    "video",
                    "num_rooms",
                    "area_total",
                    "area_living",
                    "floor_number",
                    "total_floors",
                    "year_built",
                    "renovation_type",
                    "price",
                    "currency",
                    "category",
                    "district",
                    "latitude",
                    "longitude",
                ]
            )
        return fields

    def _create_new_ad_notification_for_moderator(self, obj):
        """Уведомить модератора о новом объявлении от риелтора."""
        from project.apps.users.models import Notification

        realtor = get_realtor(obj.created_by) if obj.created_by else None
        if not realtor or not realtor.moderator:
            return
        moderator_user = realtor.moderator.user
        Notification.objects.create(
            user=moderator_user,
            title="Новое объявление на модерации",
            message=f'Риелтор {obj.created_by.get_username()} добавил объявление "{obj.title}". Требуется проверка.',
        )

    def _create_moderation_notification(self, obj):
        """Создать уведомление в админке для риелтора."""
        from project.apps.users.models import Notification

        if obj.moderation_status == Advertisement.ModerationStatus.APPROVED:
            title = "Объявление одобрено"
            message = f'Ваше объявление "{obj.title}" прошло модерацию и одобрено к публикации.'
        else:
            title = "Объявление отклонено"
            message = (
                f'Ваше объявление "{obj.title}" не прошло модерацию. '
                "Обратитесь к модератору за уточнением причин."
            )
        Notification.objects.create(
            user=obj.created_by,
            title=title,
            message=message,
        )
