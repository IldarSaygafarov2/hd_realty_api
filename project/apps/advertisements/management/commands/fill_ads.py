"""
Импорт объявлений из внешнего JSON API в локальную БД.

Ровно 20 объявлений: 10 покупка (BUY) и 10 аренда (RENT) — первые страницы API.

Slug совпадает с правилом модели: тип недвижимости (slug категории) + район
+ цена в USD (`price_usd`) + комнаты + `usd` в конце (см. `_advertisement_slug_base`).

При повторном импорте той же карточки slug сохраняется, если совпадают
категория, район, комнаты, `price_usd` и заголовок.

Данные карточки (название, описание, цена, адрес, этажи, категория, район)
берутся из API. Характеристики, парковка, класс жилья, отделка и прочие
доп. поля заполняются демо-логикой как раньше.

Фотографии скачиваются из детальной карточки (`images`) и сохраняются
в `cover_image` и `AdvertisementImage`.

`--clear` — удалить все объявления и связанные файлы (обложка, видео, галерея)
с локального хранилища перед импортом.

Запуск: python manage.py fill_ads
Перед запуском: python manage.py fill_districts_categories
"""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from project.apps.advertisements.models import (
    Advertisement,
    AdvertisementCharacteristic,
    AdvertisementImage,
    RenovationType,
    allocate_unique_advertisement_slug,
)
from project.apps.categories.models import Category
from project.apps.districts.models import District
from project.utils import listing_import

logger = logging.getLogger(__name__)

# Характеристики: (name_ru, name_uz, value_ru, value_uz) — доп. теги вне жёсткой схемы
CHARACTERISTICS_POOL = [
    ("Балкон", "Balkon", "Да", "Ha"),
    ("Лифт", "Lift", "Да", "Ha"),
    ("Материал стен", "Devor materiali", "Кирпич", "G'isht"),
    ("Охрана", "Qo'riqlash", "24/7", "24/7"),
    ("Балкон", "Balkon", "Нет", "Yo'q"),
    ("Лифт", "Lift", "Нет", "Yo'q"),
]


def _secondary_location_and_specs(
    *,
    i: int,
    district: District,
    deal_type: str,
    area_total: Decimal | None,
) -> dict:
    """Демо-значения полей модели для вторички и аренды (без ЖК/застройщика)."""
    name_ru = getattr(district, "name_ru", None) or district.name
    name_uz = getattr(district, "name_uz", None) or district.name
    floor = 1 + (i % 12)
    total = 9 + (i % 6)
    if floor > total:
        floor = total

    renovation_slugs = ("euro", "standard", "pre_finish", "no_renovation", "shell")
    renovation_objects = {
        rt.slug: rt for rt in RenovationType.objects.filter(slug__in=renovation_slugs)
    }
    renovation_cycle = tuple(renovation_objects.get(s) for s in renovation_slugs)
    parking_cycle = (
        Advertisement.ParkingType.OPEN,
        Advertisement.ParkingType.UNDERGROUND,
        Advertisement.ParkingType.NONE,
        Advertisement.ParkingType.COVERED,
        Advertisement.ParkingType.UNSPECIFIED,
    )
    class_cycle = (
        Advertisement.HousingClass.COMFORT,
        Advertisement.HousingClass.ECONOMY,
        Advertisement.HousingClass.BUSINESS,
        Advertisement.HousingClass.PREMIUM,
        Advertisement.HousingClass.UNSPECIFIED,
    )
    finish_cycle = (
        Advertisement.FinishingType.FINE,
        Advertisement.FinishingType.PRE_FINISH,
        Advertisement.FinishingType.ROUGH,
        Advertisement.FinishingType.WITHOUT,
        Advertisement.FinishingType.UNSPECIFIED,
    )

    area = area_total or Decimal("50")
    living = (area * Decimal("0.68")).quantize(Decimal("0.01"))
    addr_ru = f"ул. Намуна, д. {10 + i}, {name_ru}"
    addr_uz = f"Namuna ko'chasi, {10 + i}-uy, {name_uz}"
    lm_ru = f"Ориентир — центр района {name_ru}"
    lm_uz = f"Orientir — {name_uz} tumani markazi"
    cross_ru = "пересечение с ул. Бунёдкор"
    cross_uz = "Bunyodkor ko'chasi bilan kesishmasi"

    return {
        "residential_complex_name": "",
        "developer": "",
        "area_living": living,
        "floor_number": floor,
        "total_floors": total,
        "ceiling_height": Decimal("2.72") if i % 2 == 0 else Decimal("3.00"),
        "year_built": 2005 + (i % 18),
        "renovation_type": renovation_cycle[i % len(renovation_cycle)],
        "parking_type": parking_cycle[i % len(parking_cycle)],
        "housing_class": class_cycle[i % len(class_cycle)],
        "finishing_type": finish_cycle[i % len(finish_cycle)],
        "is_furnished": (
            True if deal_type == Advertisement.DealType.RENT else (i % 2 == 0)
        ),
        "has_commission": i % 4 == 1,
        "address": addr_ru,
        "address_ru": addr_ru,
        "address_uz": addr_uz,
        "landmark": lm_ru,
        "landmark_ru": lm_ru,
        "landmark_uz": lm_uz,
        "street_intersection": cross_ru,
        "street_intersection_ru": cross_ru,
        "street_intersection_uz": cross_uz,
    }


def _new_building_extras(*, area_total: Decimal | None, euro_renovation) -> dict:
    area = area_total or Decimal("70")
    return {
        "residential_complex_name": "Assalom Sohil",
        "developer": "Golden House",
        "parking_type": Advertisement.ParkingType.OPEN,
        "housing_class": Advertisement.HousingClass.COMFORT,
        "finishing_type": Advertisement.FinishingType.FINE,
        "is_furnished": True,
        "has_commission": False,
        "renovation_type": euro_renovation,
        "ceiling_height": Decimal("2.00"),
        "floor_number": 4,
        "total_floors": 9,
        "area_living": (area * Decimal("0.68")).quantize(Decimal("0.01")),
        "year_built": 2025,
        "landmark": "Ориентир — Узбум",
        "landmark_ru": "Ориентир — Узбум",
        "landmark_uz": "Orientir — Uzbum",
        "street_intersection": "пересечение улиц Янгизамон и Сайхун",
        "street_intersection_ru": "пересечение улиц Янгизамон и Сайхун",
        "street_intersection_uz": "Yangizamon va Sayhun ko'chalari kesishmasi",
        "address": "Мирабадский район, новостройка",
        "address_ru": "Мирабадский район, новостройка",
        "address_uz": "Mirobod tumani, yangi uy",
    }


def _deal_type_from_operation(operation_type: str, detail: dict) -> str:
    op = (operation_type or "").upper()
    if op == "RENT":
        return Advertisement.DealType.RENT
    if op == "BUY":
        return Advertisement.DealType.SALE
    text = (detail.get("operation_type") or "").lower()
    if "аренд" in text or "ijara" in text:
        return Advertisement.DealType.RENT
    return Advertisement.DealType.SALE


def _housing_market_from_detail(detail: dict) -> str:
    prop = (detail.get("property_type") or "").lower()
    if "новострой" in prop or "yangi" in prop:
        return Advertisement.HousingMarket.NEW_BUILDING
    return Advertisement.HousingMarket.SECONDARY


def _decimal_or_none(value) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _resolve_category(detail: dict, categories: list[Category]) -> Category:
    api_cat = detail.get("category") or {}
    slug = listing_import.resolve_local_slug(
        api_cat.get("slug"), listing_import.CATEGORY_SLUG_ALIASES
    )
    if slug:
        for cat in categories:
            if cat.slug == slug:
                return cat
    return categories[0]


def _resolve_district(detail: dict, districts: list[District]) -> District:
    api_dist = detail.get("district") or {}
    slug = listing_import.resolve_local_slug(
        api_dist.get("slug"), listing_import.DISTRICT_SLUG_ALIASES
    )
    if slug:
        for dist in districts:
            if dist.slug == slug:
                return dist
    return districts[0]


def _slug_for_import_listing(
    *,
    category: Category,
    district: District,
    defaults: dict,
) -> str:
    """Slug: категория + район + price_usd + комнаты (+ usd), как у модели.

    При повторном импорте той же строки API возвращаем уже существующий slug.
    """
    prior = Advertisement.objects.filter(
        category_id=category.id,
        district_id=district.id,
        num_rooms=defaults["num_rooms"],
        price_usd=defaults["price_usd"],
        title=defaults["title"],
    ).first()
    if prior and prior.slug:
        return prior.slug
    return allocate_unique_advertisement_slug(
        category_slug=category.slug,
        district_slug=district.slug,
        price_usd=defaults["price_usd"],
        price=Decimal("0"),
        currency=Advertisement.Currency.UZS,
        num_rooms=defaults["num_rooms"],
    )


def _delete_field_file(field) -> None:
    """Удалить файл с диска (ImageField / FileField), не трогая строку БД."""
    if field and getattr(field, "name", None):
        field.delete(save=False)


def _purge_advertisement_storage(ad: Advertisement) -> None:
    """Удалить с диска галерею, обложку и видео объявления; удалить строки галереи."""
    for img in list(AdvertisementImage.objects.filter(advertisement_id=ad.pk)):
        _delete_field_file(img.image)
        img.delete()
    _delete_field_file(ad.cover_image)
    _delete_field_file(ad.video)


def _build_defaults_from_api(
    *,
    detail: dict,
    operation_type: str,
    index: int,
    category: Category,
    district: District,
    euro_renovation,
) -> dict:
    deal_type = _deal_type_from_operation(operation_type, detail)
    housing_market = _housing_market_from_detail(detail)
    area_total = _decimal_or_none(detail.get("quadrature"))
    price_usd = _decimal_or_none(detail.get("price")) or Decimal("0")
    num_rooms = int(detail.get("rooms_quantity") or 1)

    title_ru = (detail.get("name") or "").strip() or f"Объявление {detail.get('id')}"
    title_uz = (detail.get("name_uz") or "").strip() or title_ru
    desc_ru = (detail.get("description") or "").strip() or title_ru
    desc_uz = (detail.get("description_uz") or "").strip() or title_uz
    addr_ru = (detail.get("address") or "").strip()
    addr_uz = (detail.get("address_uz") or "").strip()

    defaults: dict = {
        "title": title_ru,
        "title_ru": title_ru,
        "title_uz": title_uz,
        "description": desc_ru,
        "description_ru": desc_ru,
        "description_uz": desc_uz,
        "category_id": category.id,
        "district_id": district.id,
        "price_usd": price_usd,
        "deal_type": deal_type,
        "housing_market": housing_market,
        "status": Advertisement.Status.ACTIVE,
        "moderation_status": Advertisement.ModerationStatus.APPROVED,
        "is_hot": index % 2 == 0,
        "num_rooms": num_rooms,
        "area_total": area_total,
    }

    if housing_market == Advertisement.HousingMarket.NEW_BUILDING:
        defaults.update(
            _new_building_extras(area_total=area_total, euro_renovation=euro_renovation)
        )
    else:
        defaults.update(
            _secondary_location_and_specs(
                i=index,
                district=district,
                deal_type=deal_type,
                area_total=area_total,
            )
        )

    floor_from = detail.get("floor_from")
    floor_to = detail.get("floor_to")
    if floor_from is not None:
        defaults["floor_number"] = int(floor_from)
    if floor_to is not None:
        defaults["total_floors"] = int(floor_to)
    if addr_ru:
        defaults["address"] = addr_ru
        defaults["address_ru"] = addr_ru
    if addr_uz:
        defaults["address_uz"] = addr_uz

    year = detail.get("creation_year")
    if year and int(year) > 0:
        defaults["year_built"] = int(year)

    return defaults


def _attach_characteristics(ad: Advertisement, index: int) -> None:
    if ad.characteristics.exists():
        return
    pool_size = len(CHARACTERISTICS_POOL)
    for k in range(2 + (index % 3)):
        nr, nz, vr, vz = CHARACTERISTICS_POOL[(index + k) % pool_size]
        AdvertisementCharacteristic.objects.create(
            advertisement=ad,
            name=nr,
            name_ru=nr,
            name_uz=nz,
            value=vr,
            value_ru=vr,
            value_uz=vz,
        )


def _attach_images(ad: Advertisement, detail: dict, *, stdout) -> int:
    """Скачать images из API; вернуть число добавленных файлов."""
    images = detail.get("images") or []
    if not images and detail.get("preview"):
        images = [{"url": detail["preview"]}]
    if not images:
        return 0

    if ad.images.exists():
        if not ad.cover_image:
            first = ad.images.first()
            if first and first.image:
                ad.cover_image = first.image
                ad.save(update_fields=["cover_image"])
        return 0

    saved = 0
    for idx, item in enumerate(images):
        rel = (item.get("url") if isinstance(item, dict) else None) or ""
        if not rel:
            continue
        try:
            content = listing_import.download_media(rel)
        except Exception as exc:
            logger.warning("Не удалось скачать %s: %s", rel, exc)
            stdout.write(f"  ! фото не загружено: {rel} ({exc})")
            continue

        filename = listing_import.image_filename(rel)
        file_obj = ContentFile(content, name=filename)

        if idx == 0 and not ad.cover_image:
            ad.cover_image.save(filename, file_obj, save=True)
            saved += 1
            file_obj = ContentFile(content, name=filename)

        AdvertisementImage.objects.create(
            advertisement=ad,
            image=file_obj,
        )
        saved += 1

    return saved


class Command(BaseCommand):
    help = (
        "Импортирует ровно 20 объявлений из внешнего API (10 BUY + 10 RENT) "
        "и подгружает фотографии. Slug — категория + район + цена USD + комнаты."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help=(
                "Удалить все объявления и связанные файлы с диска "
                "(обложка, видео, галерея) перед импортом"
            ),
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Не скачивать фотографии",
        )

    def handle(self, *args, **options):
        categories = list(Category.objects.all())
        districts = list(District.objects.all())
        if not categories or not districts:
            self.stdout.write(
                self.style.ERROR(
                    "Сначала выполните: python manage.py fill_districts_categories"
                )
            )
            return

        euro_renovation = RenovationType.objects.filter(slug="euro").first()

        per_type = listing_import.ADS_PER_DEAL_TYPE
        skip_images = options["skip_images"]

        # Список объявлений для импорта: ровно per_type на BUY и per_type на RENT
        batches: list[tuple[str, list[dict]]] = []
        for operation_type in listing_import.OPERATION_TYPES:
            try:
                items = listing_import.fetch_advertisements_page(
                    operation_type, limit=per_type, offset=0
                )
            except listing_import.ListingsImportAPIError as exc:
                self.stdout.write(self.style.ERROR(str(exc)))
                return
            if len(items) < per_type:
                self.stdout.write(
                    self.style.ERROR(
                        f"API {operation_type}: получено {len(items)} объявлений, "
                        f"нужно ровно {per_type}. Проверьте лимит и доступность API."
                    )
                )
                return
            items = items[:per_type]
            batches.append((operation_type, items))

        expected_total = per_type * len(listing_import.OPERATION_TYPES)

        if options["clear"]:
            n = 0
            for ad in Advertisement.objects.iterator(chunk_size=20):
                _purge_advertisement_storage(ad)
                ad.delete()
                n += 1
            self.stdout.write(
                f"Удалено объявлений: {n} (файлы обложки, видео и галереи с диска удалены)"
            )

        created = 0
        updated_images = 0
        index = 0
        errors = 0

        for operation_type, items in batches:
            self.stdout.write(f"=== {operation_type} ({len(items)}) ===")
            for item in items:
                ad_id = item.get("id")
                if not ad_id:
                    self.stdout.write(
                        self.style.WARNING("  ! элемент списка без id, пропуск")
                    )
                    errors += 1
                    continue

                try:
                    detail = listing_import.fetch_advertisement_detail(int(ad_id))
                except listing_import.ListingsImportAPIError as exc:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ! id={ad_id}: деталь не получена ({exc})"
                        )
                    )
                    errors += 1
                    continue

                category = _resolve_category(detail, categories)
                district = _resolve_district(detail, districts)
                defaults = _build_defaults_from_api(
                    detail=detail,
                    operation_type=operation_type,
                    index=index,
                    category=category,
                    district=district,
                    euro_renovation=euro_renovation,
                )
                slug = _slug_for_import_listing(
                    category=category, district=district, defaults=defaults
                )

                ad, was_created = Advertisement.objects.get_or_create(
                    slug=slug,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                    self.stdout.write(f"  + {slug} — {defaults['title'][:60]}")
                else:
                    self.stdout.write(f"  = {slug} (уже есть)")

                _attach_characteristics(ad, index)

                if not skip_images:
                    n = _attach_images(ad, detail, stdout=self.stdout)
                    updated_images += n

                index += 1

        if errors or index != expected_total:
            raise CommandError(
                f"Должно быть импортировано ровно {expected_total} объявлений, "
                f"успешно обработано: {index}, ошибок: {errors}."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: создано {created}, фото загружено {updated_images}, "
                f"импортировано объявлений: {index}, всего в БД "
                f"{Advertisement.objects.count()}"
            )
        )
