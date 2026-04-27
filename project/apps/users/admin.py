from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import (
    UnfoldAdminEmailInputWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
)

from project.apps.users.utils import is_moderator, is_realtor

from .models import Moderator, Notification, Realtor, UserProfile

ROLE_NONE = ""
ROLE_MODERATOR = "moderator"
ROLE_REALTOR = "realtor"
ROLE_CHOICES = [
    (ROLE_NONE, "— Без роли —"),
    (ROLE_MODERATOR, "Модератор"),
    (ROLE_REALTOR, "Риелтор"),
]


class CustomUserCreationForm(UserCreationForm):
    """Форма добавления пользователя в админке: email, телефон, роль, куратор."""

    email = forms.EmailField(
        label="Email",
        required=False,
        widget=UnfoldAdminEmailInputWidget(),
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=32,
        required=False,
        widget=UnfoldAdminTextInputWidget(),
    )
    role = forms.ChoiceField(
        label="Роль",
        choices=ROLE_CHOICES,
        required=False,
        widget=UnfoldAdminSelectWidget(),
    )
    moderator = forms.ModelChoiceField(
        label="Модератор-куратор",
        queryset=Moderator.objects.select_related("user").all(),
        required=False,
        help_text="Обязателен при роли «Риелтор».",
        widget=UnfoldAdminSelectWidget(),
    )

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        moderator = cleaned.get("moderator")
        if role == ROLE_REALTOR and not moderator:
            raise ValidationError(
                {"moderator": "Для роли «Риелтор» обязательно укажите модератора."}
            )
        if role != ROLE_REALTOR:
            cleaned["moderator"] = None
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        email = (self.cleaned_data.get("email") or "").strip()
        if email:
            user.email = email
        if self.cleaned_data.get("role"):
            user.is_staff = True
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"phone": (self.cleaned_data.get("phone") or "").strip()},
            )
            role = self.cleaned_data.get("role")
            if role == ROLE_MODERATOR:
                Moderator.objects.get_or_create(user=user)
            elif role == ROLE_REALTOR:
                Realtor.objects.create(
                    user=user,
                    moderator=self.cleaned_data["moderator"],
                )
        return user


class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования пользователя: показывает телефон из профиля."""

    phone = forms.CharField(
        label="Телефон",
        max_length=32,
        required=False,
        widget=UnfoldAdminTextInputWidget(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            profile = getattr(self.instance, "profile", None)
            if profile is not None:
                self.fields["phone"].initial = profile.phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.update_or_create(
                user=user,
                defaults={"phone": (self.cleaned_data.get("phone") or "").strip()},
            )
        return user


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        "username",
        "email",
        "get_phone",
        "get_role",
        "is_staff",
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Личная информация",
            {"fields": ("first_name", "last_name", "email", "phone")},
        ),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            "Контакты и роль",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone",
                    "role",
                    "moderator",
                ),
            },
        ),
    )

    @admin.display(description="Телефон")
    def get_phone(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.phone if profile else ""

    @admin.display(description="Роль")
    def get_role(self, obj):
        if is_moderator(obj):
            return "Модератор"
        if is_realtor(obj):
            return "Риелтор"
        return "—"


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Moderator)
class ModeratorAdmin(ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)


@admin.register(Realtor)
class RealtorAdmin(ModelAdmin):
    list_display = ("user", "moderator")
    list_filter = ("moderator",)
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user", "moderator")


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "user", "is_read", "created_at")
    list_filter = ("is_read",)
    search_fields = ("title", "message")
    readonly_fields = ("user", "title", "message", "created_at")
    list_editable = ("is_read",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_module_permission(self, request):
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_view_permission(self, request, obj=None):
        return (
            request.user.is_superuser
            or is_realtor(request.user)
            or is_moderator(request.user)
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or (
            obj and obj.user_id == request.user.id
        )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or (
            obj and obj.user_id == request.user.id
        )
