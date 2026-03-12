from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from project.apps.users.utils import is_moderator, is_realtor

from .models import Moderator, Notification, Realtor

# Регистрация User и Group с Unfold — нужна для добавления пользователей
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


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
