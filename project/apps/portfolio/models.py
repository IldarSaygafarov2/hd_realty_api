from django.db import models

from project.infrastructure.models import TimeStampedModel


class PortfolioItem(TimeStampedModel):
    """Пример работы (запись портфолио)."""

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    video = models.FileField(
        "Видео",
        upload_to="portfolio/videos/%Y/%m/",
        blank=True,
    )
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Пример работы"
        verbose_name_plural = "Примеры работ"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PortfolioItemImage(TimeStampedModel):
    """Фотография примера работы."""

    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Пример работы",
    )
    image = models.ImageField(
        "Фотография",
        upload_to="portfolio/images/%Y/%m/",
    )

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ["id"]

    def __str__(self):
        return f"Фото #{self.pk}"


class PortfolioCompletedWork(TimeStampedModel):
    """Выполненная работа (тег «Было выполнено»)."""

    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name="completed_works",
        verbose_name="Пример работы",
    )
    title = models.CharField("Название", max_length=255)
    icon = models.CharField(
        "Иконка (emoji или CSS-класс)",
        max_length=50,
        blank=True,
        help_text="Например: 📷 или fa-camera",
    )

    class Meta:
        verbose_name = "Выполненная работа"
        verbose_name_plural = "Выполненные работы"
        ordering = ["id"]

    def __str__(self):
        return self.title
