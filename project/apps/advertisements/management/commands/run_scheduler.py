"""
Долгоживущий процесс APScheduler.
Раз в сутки в 09:00 (Asia/Tashkent) обновляет курс USD c cbu.uz
и пересчитывает цены объявлений.
"""
import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from project.apps.advertisements.services.currency import (
    update_usd_rate_and_recalculate,
)

logger = logging.getLogger(__name__)


def _job_update_usd_rate():
    try:
        rate, updated = update_usd_rate_and_recalculate()
        logger.info("scheduler: USD=%s, recalculated=%s", rate, updated)
    except Exception:
        logger.exception("scheduler: ошибка обновления курса USD")


class Command(BaseCommand):
    help = "Планировщик задач (APScheduler). Запускать как отдельный процесс/контейнер."

    def add_arguments(self, parser):
        parser.add_argument(
            "--run-now",
            action="store_true",
            help="Сразу обновить курс при старте (помимо расписания).",
        )

    def handle(self, *args, **options):
        timezone = getattr(settings, "TIME_ZONE", "UTC")
        scheduler = BlockingScheduler(timezone=timezone)

        scheduler.add_job(
            _job_update_usd_rate,
            CronTrigger(hour=9, minute=0, timezone=timezone),
            id="update_usd_rate_daily",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Scheduler started: USD rate update at 09:00 ({timezone})."
            )
        )

        if options.get("run_now"):
            _job_update_usd_rate()

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write("Scheduler stopped.")
        except Exception:
            logger.exception("scheduler: критическая ошибка, перезапуск через 30с")
            time.sleep(30)
            raise
