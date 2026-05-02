from django.db import models

from project.infrastructure.models import TimeStampedModel


class ConsultationRequest(TimeStampedModel):
    """Заявка с формы «Получите экспертную оценку»."""

    class Goal(models.TextChoices):
        BUY = "buy", "Купить"
        SELL = "sell", "Продать"

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Обработана"
        CANCELLED = "cancelled", "Отменена"

    name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=32)
    goal = models.CharField(
        "Цель",
        max_length=16,
        choices=Goal.choices,
    )
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )
    comment = models.TextField("Комментарий менеджера", blank=True)

    class Meta:
        verbose_name = "Заявка на консультацию"
        verbose_name_plural = "Заявки на консультацию"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"


class ContactRequest(TimeStampedModel):
    """Заявка с формы «Оставьте заявку — подскажем следующий шаг»."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Обработана"
        CANCELLED = "cancelled", "Отменена"

    name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=32)
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )
    comment = models.TextField("Комментарий менеджера", blank=True)

    class Meta:
        verbose_name = "Заявка на обратный звонок"
        verbose_name_plural = "Заявки на обратный звонок"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"


class NextStepRequest(TimeStampedModel):
    """Заявка с формы «Оставьте заявку — подскажем следующий шаг»."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Обработана"
        CANCELLED = "cancelled", "Отменена"

    name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=32)
    task_description = models.TextField("Описание задачи", blank=True)
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )

    class Meta:
        verbose_name = "Заявка «Подскажем следующий шаг»"
        verbose_name_plural = "Заявки «Подскажем следующий шаг»"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"


