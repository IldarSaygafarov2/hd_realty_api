"""
Заполнение районов Ташкента (12 шт.) и категорий недвижимости.
Запуск: python manage.py fill_districts_categories
"""
from django.core.management.base import BaseCommand

from project.apps.categories.models import Category
from project.apps.districts.models import District


# 12 районов города Ташкент: (slug, name_ru, name_uz)
DISTRICTS = [
    ("yangihayot", "Янгихаётский район", "Yangi hayot tumani"),
    ("yashnobod", "Яшнабадский район", "Yashnobod tumani"),
    ("yakkasaroy", "Яккасарайский район", "Yakkasaroy tumani"),
    ("yunusobod", "Юнусабадский район", "Yunusobod tumani"),
    ("shayxontohur", "Шайхантаурский район", "Shayxontohur tumani"),
    ("chilonzor", "Чиланзарский район", "Chilonzor tumani"),
    ("olmazor", "Алмазарский район", "Olmazor tumani"),
    ("sergeli", "Сергелийский район", "Sergeli tumani"),
    ("mirobod", "Мирабадский район", "Mirobod tumani"),
    ("mirzo-ulugbek", "Мирзо-Улугбекский район", "Mirzo Ulug'bek tumani"),
    ("bektemir", "Бектемирский район", "Bektemir tumani"),
    ("uchtepa", "Учтепинский район", "Uchtepa tumani"),
]

# slug, name_ru, name_uz
CATEGORIES = [
    ("kvartira", "Квартира", "Kvartira"),
    ("dom", "Дом", "Uy"),
    ("uchastok", "Участок", "Er uchasti"),
    ("kommercheskaya", "Коммерческая недвижимость", "Tijorat ko'chmas mulki"),
]


class Command(BaseCommand):
    help = "Заполняет таблицы районов (12 районов Ташкента) и категорий"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить существующие районы и категории перед заполнением",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            District.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Существующие районы и категории удалены.")

        # Районы
        created_d = 0
        for slug, name_ru, name_uz in DISTRICTS:
            _, was_created = District.objects.get_or_create(
                slug=slug,
                defaults={"name": name_ru, "name_ru": name_ru, "name_uz": name_uz},
            )
            if was_created:
                created_d += 1
        self.stdout.write(
            self.style.SUCCESS(f"Районы: создано {created_d}, всего {District.objects.count()}")
        )

        # Категории
        created_c = 0
        for slug, name_ru, name_uz in CATEGORIES:
            _, was_created = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name_ru, "name_ru": name_ru, "name_uz": name_uz},
            )
            if was_created:
                created_c += 1
        self.stdout.write(
            self.style.SUCCESS(f"Категории: создано {created_c}, всего {Category.objects.count()}")
        )
