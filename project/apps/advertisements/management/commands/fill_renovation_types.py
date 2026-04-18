"""
Заполнение справочника типов ремонта для жилых помещений.
Запуск: python manage.py fill_renovation_types
"""
from django.core.management.base import BaseCommand

from project.apps.advertisements.models import RenovationType


# slug, name_ru, name_uz
RENOVATION_TYPES = [
    ("no_renovation", "Без ремонта", "Ta'mirsiz"),
    ("shell", "Черновая отделка", "Qoʻpol qoplama"),
    ("pre_finish", "Предчистовая отделка", "Yarim tayyor qoplama"),
    ("cosmetic", "Косметический ремонт", "Kosmetik taʼmir"),
    ("standard", "Стандартный ремонт", "Standart taʼmir"),
    ("euro", "Евроремонт", "Evroʻtamir"),
    ("designer", "Дизайнерский ремонт", "Dizaynerlik taʼmiri"),
    ("author", "Авторский проект", "Mualliflik loyihasi"),
]


class Command(BaseCommand):
    help = "Заполняет справочник типов ремонта для жилых помещений."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить все типы ремонта перед заполнением",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = RenovationType.objects.all().delete()
            self.stdout.write(f"Удалено типов ремонта: {deleted}")

        created = 0
        for slug, name_ru, name_uz in RENOVATION_TYPES:
            _, was_created = RenovationType.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name_ru,
                    "name_ru": name_ru,
                    "name_uz": name_uz,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Типы ремонта: создано {created}, всего {RenovationType.objects.count()}"
            )
        )
