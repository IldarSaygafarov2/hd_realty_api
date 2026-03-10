from decimal import Decimal

from django.db import models

from project.infrastructure.models import TimeStampedModel


class Advertisement(TimeStampedModel):
    """Объявление о недвижимости."""

    class Status(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        ACTIVE = 1, "Активно"
        PENDING = 2, "На модерации"
        SOLD = 3, "Продано"
        ARCHIVED = 4, "В архиве"

    class RenovationType(models.TextChoices):
        RENOVATION = "renovation", "Ремонт"
        PRE_FINISHED = "pre_finished", "Предчистовая"
        SHELL = "shell", "Коробка"
        NONE = "none", "Без ремонта"

    class Currency(models.TextChoices):
        USD = "USD", "$"
        UZS = "UZS", "сум"

    # Основное
    title = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True, db_index=True)
    description = models.TextField("Описание", blank=True)
    status = models.PositiveSmallIntegerField(
        "Статус", choices=Status.choices, default=Status.DRAFT
    )

    # Цена
    price = models.DecimalField(
        "Цена", max_digits=12, decimal_places=0, default=Decimal("0")
    )
    currency = models.CharField(
        "Валюта", max_length=3, choices=Currency.choices, default=Currency.USD
    )

    # Характеристики
    num_rooms = models.PositiveSmallIntegerField("Количество комнат", default=1)
    area_total = models.DecimalField(
        "Общая площадь (м²)", max_digits=8, decimal_places=2, null=True, blank=True
    )
    area_living = models.DecimalField(
        "Жилая площадь (м²)", max_digits=8, decimal_places=2, null=True, blank=True
    )
    floor_number = models.PositiveSmallIntegerField(
        "Этаж", null=True, blank=True
    )
    total_floors = models.PositiveSmallIntegerField(
        "Всего этажей", null=True, blank=True
    )
    ceiling_height = models.DecimalField(
        "Высота потолков (м)", max_digits=4, decimal_places=2, null=True, blank=True
    )
    year_built = models.PositiveIntegerField(
        "Год постройки", null=True, blank=True
    )
    renovation_type = models.CharField(
        "Тип ремонта",
        max_length=20,
        choices=RenovationType.choices,
        default=RenovationType.NONE,
        blank=True,
    )

    # Расположение
    address = models.CharField("Адрес", max_length=500, blank=True)
    latitude = models.DecimalField(
        "Широта", max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        "Долгота", max_digits=9, decimal_places=6, null=True, blank=True
    )

    # Связи
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name="advertisements",
    )
    district = models.ForeignKey(
        "districts.District",
        on_delete=models.CASCADE,
        verbose_name="Район",
        related_name="advertisements",
    )

    # Служебное
    views_count = models.PositiveIntegerField("Просмотры", default=0)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AdvertisementImage(TimeStampedModel):
    """Изображение объявления."""

    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        verbose_name="Объявление",
        related_name="images",
    )
    image = models.ImageField(
        "Изображение", upload_to="advertisements/%Y/%m/", blank=True
    )

    class Meta:
        verbose_name = "Изображение объявления"
        verbose_name_plural = "Изображения объявлений"
        ordering = ["id"]

    def __str__(self):
        return f"Изображение #{self.pk}"


class AdvertisementCharacteristic(TimeStampedModel):
    """Характеристика объявления (название — значение)."""

    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        verbose_name="Объявление",
        related_name="characteristics",
    )
    name = models.CharField("Название", max_length=255)
    value = models.CharField("Значение", max_length=255)

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        ordering = ["id"]

    def __str__(self):
        return f"{self.name}: {self.value}"
