from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from project.infrastructure.models import TimeStampedModel


def _advertisement_slug_base(
    category_slug: str,
    district_slug: str,
    price: Decimal,
    num_rooms: int,
    currency: str,
) -> str:
    """Составная часть slug: категория + район + цена + комнаты + валюта (уникальность по валюте)."""
    price_int = int(price)
    curr = (currency or "USD").lower()
    return f"{category_slug}-{district_slug}-{price_int}-{num_rooms}-{curr}"


class Advertisement(TimeStampedModel):
    """Объявление о недвижимости."""

    class Status(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        ACTIVE = 1, "Активно"
        PENDING = 2, "На модерации"
        SOLD = 3, "Продано"
        ARCHIVED = 4, "В архиве"

    class ModerationStatus(models.IntegerChoices):
        PENDING = 0, "Ожидает модерации"
        APPROVED = 1, "Одобрено"
        REJECTED = 2, "Отклонено"

    class RenovationType(models.TextChoices):
        RENOVATION = "renovation", "Ремонт"
        PRE_FINISHED = "pre_finished", "Предчистовая"
        SHELL = "shell", "Коробка"
        NONE = "none", "Без ремонта"

    class Currency(models.TextChoices):
        USD = "USD", "$"
        UZS = "UZS", "сум"

    class DealType(models.TextChoices):
        """Аренда / покупка (как на витрине поиска)."""

        RENT = "rent", "Аренда"
        SALE = "sale", "Покупка"

    class HousingMarket(models.TextChoices):
        """Новостройка или вторичный рынок."""

        NEW_BUILDING = "new_building", "Новостройка"
        SECONDARY = "secondary", "Вторичка"

    # Основное
    is_hot = models.BooleanField(
        "Горячее объявление",
        default=False,
        help_text="Горячее объявление?",
    )
    title = models.CharField("Название", max_length=255)
    cover_image = models.ImageField(
        "Фото заставки", upload_to="advertisements/covers/%Y/%m/", blank=True
    )
    video = models.FileField(
        "Видео", upload_to="advertisements/videos/%Y/%m/", blank=True
    )
    slug = models.SlugField(
        "Slug",
        max_length=255,
        unique=True,
        db_index=True,
        blank=True,
        help_text="Пусто при создании — из категории, района, цены, комнат и валюты.",
    )
    description = models.TextField("Описание", blank=True)
    status = models.PositiveSmallIntegerField(
        "Статус", choices=Status.choices, default=Status.DRAFT
    )
    moderation_status = models.PositiveSmallIntegerField(
        "Модерация",
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
    )
    deal_type = models.CharField(
        "Тип сделки",
        max_length=10,
        choices=DealType.choices,
        default=DealType.SALE,
        db_index=True,
    )
    housing_market = models.CharField(
        "Рынок жилья",
        max_length=20,
        choices=HousingMarket.choices,
        default=HousingMarket.SECONDARY,
        db_index=True,
        help_text="Новостройка или вторичка",
    )

    # Цена
    price = models.DecimalField(
        "Цена", max_digits=12, decimal_places=0, default=Decimal("0")
    )
    currency = models.CharField(
        "Валюта", max_length=3, choices=Currency.choices, default=Currency.USD
    )

    # Характеристики (0 = студия)
    num_rooms = models.SmallIntegerField(
        "Количество комнат",
        default=1,
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="0 — студия",
    )
    area_total = models.DecimalField(
        "Общая площадь (м²)", max_digits=8, decimal_places=2, null=True, blank=True
    )
    area_living = models.DecimalField(
        "Жилая площадь (м²)", max_digits=8, decimal_places=2, null=True, blank=True
    )
    floor_number = models.PositiveSmallIntegerField("Этаж", null=True, blank=True)
    total_floors = models.PositiveSmallIntegerField(
        "Всего этажей", null=True, blank=True
    )
    ceiling_height = models.DecimalField(
        "Высота потолков (м)", max_digits=4, decimal_places=2, null=True, blank=True
    )
    year_built = models.PositiveIntegerField("Год постройки", null=True, blank=True)
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
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advertisements",
        verbose_name="Создал",
    )
    views_count = models.PositiveIntegerField("Просмотры", default=0)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def _generate_unique_slug(self) -> str:
        if not self.category_id or not self.district_id:
            from django.utils.crypto import get_random_string

            return f"ad-{get_random_string(12)}"
        cat_slug = self.category.slug
        dist_slug = self.district.slug
        base = _advertisement_slug_base(
            cat_slug, dist_slug, self.price, self.num_rooms, self.currency
        )
        candidate = base
        n = 0
        qs = Advertisement.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.filter(slug=candidate).exists():
            n += 1
            suffix = f"-{n}"
            max_len = 255 - len(suffix)
            candidate = (base[:max_len] if len(base) > max_len else base) + suffix
        return candidate[:255]

    def save(self, *args, **kwargs):
        if self._state.adding and not (self.slug and str(self.slug).strip()):
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


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
