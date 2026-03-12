from django.conf import settings
from django.db import models


class Moderator(models.Model):
    """Модератор — привязан к пользователю Django."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moderator_profile",
        verbose_name="Пользователь",
    )

    class Meta:
        verbose_name = "Модератор"
        verbose_name_plural = "Модераторы"

    def __str__(self):
        return str(self.user)


class Realtor(models.Model):
    """Риелтор — привязан к пользователю и модератору."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="realtor_profile",
        verbose_name="Пользователь",
    )
    moderator = models.ForeignKey(
        Moderator,
        on_delete=models.CASCADE,
        related_name="realtors",
        verbose_name="Модератор",
    )

    class Meta:
        verbose_name = "Риелтор"
        verbose_name_plural = "Риелторы"

    def __str__(self):
        return str(self.user)


class Notification(models.Model):
    """Уведомление для пользователя (показывается в админке)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Получатель",
    )
    title = models.CharField("Заголовок", max_length=255)
    message = models.TextField("Сообщение")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
