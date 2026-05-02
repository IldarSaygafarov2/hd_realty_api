"""
Получение курса USD c cbu.uz и пересчёт цен в объявлениях.

Курс хранится глобально в django-constance (`USD_RATE`).
"""
from __future__ import annotations

import json
import logging
import urllib.request
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from constance import config
from django.db import transaction

from project.apps.advertisements.models import Advertisement

logger = logging.getLogger(__name__)

CBU_URL = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"
USD_CODE = "USD"


def fetch_usd_rate_from_cbu(timeout: float = 15.0) -> tuple[Decimal, date | None]:
    """Загрузить курс USD c cbu.uz, нормализуя к курсу за 1 USD.

    Возвращает (rate_per_usd, source_date).
    """
    request = urllib.request.Request(
        CBU_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; hd-realty/1.0)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, list):
        raise ValueError("Неожиданный формат ответа cbu.uz")

    for item in data:
        ccy = (item.get("Ccy") or "").upper()
        if ccy != USD_CODE:
            continue
        rate_raw = (item.get("Rate") or "").replace(",", ".").strip()
        try:
            rate = Decimal(rate_raw)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Не удалось распарсить курс USD: {rate_raw!r}") from exc
        try:
            nominal = int(item.get("Nominal") or 1)
        except (TypeError, ValueError):
            nominal = 1
        rate_per_unit = rate / Decimal(nominal or 1)

        source_date: date | None = None
        date_raw = (item.get("Date") or "").strip()
        if date_raw:
            for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
                try:
                    source_date = datetime.strptime(date_raw, fmt).date()
                    break
                except ValueError:
                    continue
        return rate_per_unit, source_date

    raise ValueError("Курс USD не найден в ответе cbu.uz")


def get_current_usd_rate() -> Decimal | None:
    """Текущий курс 1 USD в UZS из constance."""
    raw = getattr(config, "USD_RATE", None)
    if raw is None:
        return None
    try:
        value = Decimal(raw) if not isinstance(raw, Decimal) else raw
    except (InvalidOperation, ValueError, TypeError):
        return None
    return value if value > 0 else None


def save_usd_rate(rate_per_unit: Decimal, source_date: date | None) -> None:
    """Записать актуальный курс USD в constance."""
    config.USD_RATE = rate_per_unit


@transaction.atomic
def recalculate_advertisement_prices_uzs() -> int:
    """Пересчитать `price` всех объявлений из `price_usd` по текущему курсу USD."""
    rate = get_current_usd_rate()
    if rate is None:
        logger.warning("USD_RATE не задан — пересчёт пропущен.")
        return 0

    updated = 0
    qs = Advertisement.objects.filter(price_usd__isnull=False).only(
        "id", "price_usd", "price", "currency"
    )
    for ad in qs.iterator(chunk_size=500):
        new_price = (Decimal(ad.price_usd) * rate).quantize(Decimal("1"))
        if ad.price != new_price or ad.currency != Advertisement.Currency.UZS:
            Advertisement.objects.filter(pk=ad.pk).update(
                price=new_price,
                currency=Advertisement.Currency.UZS,
            )
            updated += 1
    return updated


def update_usd_rate_and_recalculate() -> tuple[Decimal, int]:
    """Полный цикл: получить курс c cbu.uz, сохранить в constance, пересчитать цены."""
    rate_per_unit, source_date = fetch_usd_rate_from_cbu()
    save_usd_rate(rate_per_unit, source_date)
    updated = recalculate_advertisement_prices_uzs()
    logger.info(
        "USD rate updated: %s UZS/USD (date=%s); ads recalculated: %s",
        rate_per_unit,
        source_date,
        updated,
    )
    return rate_per_unit, updated
