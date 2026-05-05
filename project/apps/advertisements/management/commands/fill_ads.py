"""
Заполнение таблицы объявлений: 10 объявлений, в 5 из них is_hot=True.
Поля соответствуют модели Advertisement (в т.ч. парковка, класс жилья, отделка, ЖК).

Цена задаётся в USD (`price_usd`); цена в UZS (`price`) автоматически
пересчитывается в `Advertisement.save()` по текущему курсу из constance.

Slug формируется как у модели: категория-район-price_usd-комнаты-usd.
Запуск: python manage.py fill_ads
Перед запуском выполните: python manage.py fill_districts_categories
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from project.apps.advertisements.models import (
    Advertisement,
    AdvertisementCharacteristic,
    RenovationType,
    _advertisement_slug_base,
)
from project.apps.categories.models import Category
from project.apps.districts.models import District


# Характеристики: (name_ru, name_uz, value_ru, value_uz) — доп. теги вне жёсткой схемы
CHARACTERISTICS_POOL = [
    ("Балкон", "Balkon", "Да", "Ha"),
    ("Лифт", "Lift", "Да", "Ha"),
    ("Материал стен", "Devor materiali", "Кирпич", "G'isht"),
    ("Охрана", "Qo'riqlash", "24/7", "24/7"),
    ("Балкон", "Balkon", "Нет", "Yo'q"),
    ("Лифт", "Lift", "Нет", "Yo'q"),
]

# title_ru, title_uz, is_hot, num_rooms (0=студия), deal_type, housing_market
ADS_DATA = [
    (
        "3-комнатная квартира в Юнусабаде",
        "Yunusobodda 3 xonali kvartira",
        True,
        3,
        Advertisement.DealType.SALE,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Продаётся дом в Чиланзаре",
        "Chilonzorda uy sotiladi",
        False,
        5,
        Advertisement.DealType.SALE,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Уютная 2-комнатная в Мирабаде",
        "Mirobodda 2 xonali kvartira",
        True,
        2,
        Advertisement.DealType.RENT,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Квартира с ремонтом, Сергели",
        "Sergelida ta'mirlangan kvartira",
        False,
        2,
        Advertisement.DealType.SALE,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Горячее предложение: 4 комнаты Яккасарай",
        "Yakkasaroy 4 xona",
        True,
        4,
        Advertisement.DealType.SALE,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Участок под строительство, Бектемир",
        "Bektemir qurilish uchun joy",
        False,
        1,
        Advertisement.DealType.SALE,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Студия в центре, Шайхантаур",
        "Shayxontohur markazida studiya",
        True,
        0,
        Advertisement.DealType.RENT,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Дом с участком, Учтепа",
        "Uchtepada uy va uchastka",
        False,
        4,
        Advertisement.DealType.SALE,
        Advertisement.HousingMarket.SECONDARY,
    ),
    (
        "Новостройка Алмазар, 3 комнаты",
        "Olmazor yangi uy 3 xona",
        True,
        3,
        Advertisement.DealType.SALE,
        Advertisement.HousingMarket.NEW_BUILDING,
    ),
    (
        "Коммерческая площадь Яшнабад",
        "Yashnobodda tijorat maydoni",
        False,
        1,
        Advertisement.DealType.RENT,
        Advertisement.HousingMarket.SECONDARY,
    ),
]


def _secondary_location_and_specs(
    *,
    i: int,
    district: District,
    deal_type: str,
    area_total: Decimal,
) -> dict:
    """Демо-значения полей модели для вторички и аренды (без ЖК/застройщика)."""
    name_ru = district.name_ru or district.name
    name_uz = district.name_uz or district.name
    floor = 1 + (i % 12)
    total = 9 + (i % 6)
    if floor > total:
        floor = total

    renovation_slugs = ("euro", "standard", "pre_finish", "no_renovation", "shell")
    renovation_objects = {rt.slug: rt for rt in RenovationType.objects.filter(slug__in=renovation_slugs)}
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

    living = (area_total * Decimal("0.68")).quantize(Decimal("0.01"))
    addr_ru = f"ул. Намуна, д. {10 + i}, {name_ru}"
    addr_uz = f"Namuna ko'chasi, {10 + i}-uy, {name_uz}"
    lm_ru = f"Ориентир — центр района {name_ru}"
    lm_uz = f"Orientir — {name_uz} tumani markazi"
    cross_ru = f"пересечение с ул. Бунёдкор"
    cross_uz = f"Bunyodkor ko'chasi bilan kesishmasi"

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
        "is_furnished": True if deal_type == Advertisement.DealType.RENT else (i % 2 == 0),
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


def _new_building_extras(*, area_total: Decimal, euro_renovation) -> dict:
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
        "area_living": (area_total * Decimal("0.68")).quantize(Decimal("0.01")),
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


def _allocate_unique_slug(
    *,
    category: Category,
    district: District,
    price: Decimal,
    num_rooms: int,
    currency: str,
) -> str:
    """Тот же паттерн уникальности, что в Advertisement._generate_unique_slug."""
    base = _advertisement_slug_base(
        category.slug, district.slug, price, num_rooms, currency
    )
    candidate = base
    n = 0
    while Advertisement.objects.filter(slug=candidate).exists():
        n += 1
        suffix = f"-{n}"
        max_len = 255 - len(suffix)
        candidate = (base[:max_len] if len(base) > max_len else base) + suffix
    return candidate[:255]


class Command(BaseCommand):
    help = "Добавляет демо-объявления под текущую модель (в т.ч. ЖК, парковка, отделка)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить все объявления перед созданием",
        )

    def handle(self, *args, **options):
        categories = list(Category.objects.all())
        districts = list(District.objects.all())
        if not categories or not districts:
            self.stdout.write(
                self.style.ERROR("Сначала выполните: python manage.py fill_districts_categories")
            )
            return

        euro_renovation = RenovationType.objects.filter(slug="euro").first()

        if options["clear"]:
            deleted, _ = Advertisement.objects.all().delete()
            self.stdout.write(f"Удалено объявлений: {deleted}")

        created = 0
        for i, row in enumerate(ADS_DATA):
            title_ru, title_uz, is_hot, num_rooms, deal_type, housing_market = row
            cat = categories[i % len(categories)]
            dist = districts[i % len(districts)]
            # Цена задаётся в USD; UZS-эквивалент пересчитает Advertisement.save().
            price_usd = Decimal(30_000 + i * 10_000)
            area_total = Decimal(50 + i * 10)
            slug = _allocate_unique_slug(
                category=cat,
                district=dist,
                price=price_usd,
                num_rooms=num_rooms,
                currency=Advertisement.Currency.USD.value,
            )
            defaults = {
                "title": title_ru,
                "title_ru": title_ru,
                "title_uz": title_uz,
                "description": f"Описание объявления: {title_ru}",
                "description_ru": f"Описание объявления: {title_ru}",
                "description_uz": f"Tavsif: {title_uz}",
                "category_id": cat.id,
                "district_id": dist.id,
                "price_usd": price_usd,
                "deal_type": deal_type,
                "housing_market": housing_market,
                "status": Advertisement.Status.ACTIVE,
                "moderation_status": Advertisement.ModerationStatus.APPROVED,
                "is_hot": is_hot,
                "num_rooms": num_rooms,
                "area_total": area_total,
            }
            if housing_market == Advertisement.HousingMarket.NEW_BUILDING:
                defaults.update(_new_building_extras(area_total=area_total, euro_renovation=euro_renovation))
            else:
                defaults.update(
                    _secondary_location_and_specs(
                        i=i,
                        district=dist,
                        deal_type=deal_type,
                        area_total=area_total,
                    )
                )

            ad, was_created = Advertisement.objects.get_or_create(
                slug=slug,
                defaults=defaults,
            )
            if was_created:
                created += 1

            if ad.characteristics.exists():
                continue
            pool_size = len(CHARACTERISTICS_POOL)
            for k in range(2 + (i % 3)):
                nr, nz, vr, vz = CHARACTERISTICS_POOL[(i + k) % pool_size]
                AdvertisementCharacteristic.objects.create(
                    advertisement=ad,
                    name=nr,
                    name_ru=nr,
                    name_uz=nz,
                    value=vr,
                    value_ru=vr,
                    value_uz=vz,
                )

        self.stdout.write(
            self.style.SUCCESS(f"Объявления: создано {created}, всего {Advertisement.objects.count()}")
        )
