"""
Сигналы приложения advertisements.

Слушаем изменение значения `USD_RATE` в django-constance (через админ-панель)
и пересчитываем `price` (UZS) у всех объявлений из их `price_usd`.
"""
from __future__ import annotations

import logging

from django.db import transaction
from django.dispatch import receiver

from constance.signals import config_updated

logger = logging.getLogger(__name__)


@receiver(config_updated)
def recalculate_ads_on_usd_rate_change(sender, key, old_value, new_value, **kwargs):
    """Когда меняется `USD_RATE` в админке constance — пересчитать цены объявлений."""
    if key != "USD_RATE":
        return
    if old_value == new_value:
        return

    from project.apps.advertisements.services.currency import (
        recalculate_advertisement_prices_uzs,
    )

    def _run() -> None:
        try:
            updated = recalculate_advertisement_prices_uzs()
            logger.info(
                "USD_RATE изменён через админку (%s -> %s). Пересчитано объявлений: %s",
                old_value,
                new_value,
                updated,
            )
        except Exception:
            logger.exception("Не удалось пересчитать цены объявлений после смены USD_RATE")

    transaction.on_commit(_run)
