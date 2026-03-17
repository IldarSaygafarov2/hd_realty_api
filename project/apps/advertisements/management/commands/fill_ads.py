"""
Заполнение таблицы объявлений: 10 объявлений, в 5 из них is_hot=True.
Для каждого объявления создаются характеристики.
Запуск: python manage.py fill_ads
Перед запуском выполните: python manage.py fill_districts_categories
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from project.apps.advertisements.models import Advertisement, AdvertisementCharacteristic
from project.apps.categories.models import Category
from project.apps.districts.models import District


# Характеристики: (name_ru, name_uz, value_ru, value_uz) — для разнообразия берём по индексу
CHARACTERISTICS_POOL = [
    ("Тип ремонта", "Ta'mir turi", "Евроремонт", "Evro ta'mir"),
    ("Балкон", "Balkon", "Да", "Ha"),
    ("Лифт", "Lift", "Да", "Ha"),
    ("Парковка", "Avtoturargoh", "Подземная", "Yer ostida"),
    ("Год постройки", "Qurilish yili", "2020", "2020"),
    ("Материал стен", "Devor materiali", "Кирпич", "G'isht"),
    ("Охрана", "Qo'riqlash", "24/7", "24/7"),
    ("Балкон", "Balkon", "Нет", "Yo'q"),
    ("Лифт", "Lift", "Нет", "Yo'q"),
    ("Тип ремонта", "Ta'mir turi", "Без ремонта", "Ta'mirsiz"),
]

# 10 объявлений: slug, заголовок (ru, uz), is_hot
ADS_DATA = [
    ("kvartira-yunusobod-3kom", "3-комнатная квартира в Юнусабаде", "Yunusobodda 3 xonali kvartira", True),
    ("dom-chilonzor", "Продаётся дом в Чиланзаре", "Chilonzorda uy sotiladi", False),
    ("kvartira-mirobod-2kom", "Уютная 2-комнатная в Мирабаде", "Mirobodda 2 xonali kvartira", True),
    ("kvartira-sergeli-remont", "Квартира с ремонтом, Сергели", "Sergelida ta'mirlangan kvartira", False),
    ("kvartira-yakkasaroy-4kom", "Горячее предложение: 4 комнаты Яккасарай", "Yakkasaroy 4 xona", True),
    ("uchastok-bektemir", "Участок под строительство, Бектемир", "Bektemir qurilish uchun joy", False),
    ("studiya-shayxontohur", "Студия в центре, Шайхантаур", "Shayxontohur markazida studiya", True),
    ("dom-uchtepa-uchastok", "Дом с участком, Учтепа", "Uchtepada uy va uchastka", False),
    ("novostroyka-olmazor-3kom", "Новостройка Алмазар, 3 комнаты", "Olmazor yangi uy 3 xona", True),
    ("kommercheskaya-yashnobod", "Коммерческая площадь Яшнабад", "Yashnobodda tijorat maydoni", False),
]


class Command(BaseCommand):
    help = "Добавляет 10 объявлений (в 5 is_hot=True). Требуются районы и категории."

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

        if options["clear"]:
            deleted, _ = Advertisement.objects.all().delete()
            self.stdout.write(f"Удалено объявлений: {deleted}")

        created = 0
        for i, (slug, title_ru, title_uz, is_hot) in enumerate(ADS_DATA):
            ad, was_created = Advertisement.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title_ru,
                    "title_ru": title_ru,
                    "title_uz": title_uz,
                    "description": f"Описание объявления: {title_ru}",
                    "description_ru": f"Описание объявления: {title_ru}",
                    "description_uz": f"Tavsif: {title_uz}",
                    "address": "",
                    "address_ru": "",
                    "address_uz": "",
                    "category_id": categories[i % len(categories)].id,
                    "district_id": districts[i % len(districts)].id,
                    "price": Decimal(30_000 + i * 10_000),
                    "currency": Advertisement.Currency.USD,
                    "status": Advertisement.Status.ACTIVE,
                    "moderation_status": Advertisement.ModerationStatus.APPROVED,
                    "is_hot": is_hot,
                    "num_rooms": (i % 4) + 1,
                    "area_total": Decimal(50 + i * 10),
                },
            )
            if was_created:
                created += 1

            # Заполняем характеристики только если их ещё нет (идемпотентность)
            if ad.characteristics.exists():
                continue
            # Для каждого объявления добавляем 3–5 характеристик из пула (по индексу)
            pool_size = len(CHARACTERISTICS_POOL)
            for k in range(3 + (i % 3)):
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
