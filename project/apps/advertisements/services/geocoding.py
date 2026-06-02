"""Геокодинг адресов объявлений через geopy."""

from __future__ import annotations

import logging
from decimal import Decimal

from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)

_GEOCODER = Nominatim(user_agent="hd-realty-geocoder")
_GEOCODE = RateLimiter(
    _GEOCODER.geocode,
    min_delay_seconds=1.0,
    swallow_exceptions=False,
)


def geocode_address(address: str) -> tuple[Decimal, Decimal] | None:
    """Вернуть координаты (lat, lon) для адреса или None, если не найдено."""
    query = (address or "").strip()
    if not query:
        return None
    try:
        location = _GEOCODE(query, timeout=15)
    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as exc:
        logger.warning("Геокодинг недоступен для '%s': %s", query, exc)
        return None
    except Exception:
        logger.exception("Неожиданная ошибка геокодинга для '%s'", query)
        return None
    if location is None:
        return None
    return (
        Decimal(str(location.latitude)),
        Decimal(str(location.longitude)),
    )
