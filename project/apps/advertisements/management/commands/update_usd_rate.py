from django.core.management.base import BaseCommand

from project.apps.advertisements.services.currency import (
    update_usd_rate_and_recalculate,
)


class Command(BaseCommand):
    help = "Загрузить актуальный курс USD c cbu.uz и пересчитать цены объявлений."

    def handle(self, *args, **options):
        try:
            rate, updated = update_usd_rate_and_recalculate()
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Не удалось обновить курс: {exc}"))
            raise
        self.stdout.write(
            self.style.SUCCESS(
                f"USD = {rate} UZS; обновлено объявлений: {updated}."
            )
        )
