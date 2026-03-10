from django.db import models

from project.infrastructure.models import TimeStampedModel


class District(TimeStampedModel):
    """Район."""

    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True)

    class Meta:
        verbose_name = "Район"
        verbose_name_plural = "Районы"
        ordering = ["name"]

    def __str__(self):
        return self.name
