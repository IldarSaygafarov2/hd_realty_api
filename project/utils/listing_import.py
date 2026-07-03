"""HTTP-клиент для импорта объявлений из внешнего JSON API."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)

# Базовый хост и API (источник каталога).
BASE_SITE_URL = "https://vitrina-admin.uz"
BASE_URL = "https://vitrina-admin.uz/api/v1"
OPERATION_TYPES = ("BUY", "RENT")
DEFAULT_PAGE_SIZE = 15
# Импорт fill_ads: ровно столько объявлений на тип сделки (всего 20).
ADS_PER_DEAL_TYPE = 20

# slug API -> slug в нашей БД (fill_districts_categories)
DISTRICT_SLUG_ALIASES: dict[str, str] = {
    "mirabadskii-raion": "mirobod",
    "mirzo-ulugbekskii-raion": "mirzo-ulugbek",
    "yunusabadskii-raion": "yunusobod",
    "chilonzorskii-raion": "chilonzor",
    "yakkasarayskii-raion": "yakkasaroy",
    "yashnabadskii-raion": "yashnobod",
    "shaykhantakhurskii-raion": "shayxontohur",
    "almazarskii-raion": "olmazor",
    "sergeliiskii-raion": "sergeli",
    "bektemirskii-raion": "bektemir",
    "uchtepinskii-raion": "uchtepa",
    "yangihayotskii-raion": "yangihayot",
}

CATEGORY_SLUG_ALIASES: dict[str, str] = {
    "kvartiry": "kvartira",
    "doma": "dom",
    "uchastki": "uchastok",
    "kommercheskaya-nedvizhimost": "kommercheskaya",
}


class ListingsImportAPIError(Exception):
    """Ошибка запроса к внешнему API каталога."""


def _get_json(url: str, *, timeout: float = 30.0) -> dict | list:
    response = requests.get(
        url,
        headers={"Accept": "application/json"},
        timeout=timeout,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise ListingsImportAPIError(f"HTTP {response.status_code} для {url}") from exc
    payload = response.json()
    if not isinstance(payload, (dict, list)):
        raise ListingsImportAPIError(f"Неожиданный JSON для {url}")
    return payload


def media_absolute_url(relative_path: str) -> str:
    """Собрать абсолютный URL файла на стороне источника."""
    path = (relative_path or "").strip().lstrip("/")
    return urljoin(f"{BASE_SITE_URL}/", path)


def fetch_advertisements_page(
    operation_type: str,
    *,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
) -> list[dict]:
    """Список объявлений (одна страница)."""
    url = (
        f"{BASE_URL}/advertisements/"
        f"?operation_type={operation_type}&limit={limit}&offset={offset}"
    )
    payload = _get_json(url)
    if not isinstance(payload, dict):
        raise ListingsImportAPIError("Список объявлений: ожидался объект с results")
    results = payload.get("results")
    if not isinstance(results, list):
        raise ListingsImportAPIError("Список объявлений: нет поля results")
    return results


def iter_advertisements(
    operation_type: str,
    *,
    limit: int = DEFAULT_PAGE_SIZE,
    max_pages: int | None = None,
) -> Iterator[dict]:
    """Пагинация по всем объявлениям operation_type."""
    offset = 0
    page = 0
    while True:
        if max_pages is not None and page >= max_pages:
            break
        batch = fetch_advertisements_page(operation_type, limit=limit, offset=offset)
        if not batch:
            break
        yield from batch
        if len(batch) < limit:
            break
        offset += limit
        page += 1


def fetch_advertisement_detail(advertisement_id: int) -> dict:
    """Детальная карточка объявления (включая images)."""
    url = f"{BASE_URL}/advertisements/{advertisement_id}/"
    payload = _get_json(url)
    if not isinstance(payload, dict):
        raise ListingsImportAPIError(
            f"Деталь объявления {advertisement_id}: ожидался объект"
        )
    return payload


def download_media(relative_path: str, *, timeout: float = 60.0) -> bytes:
    """Скачать файл по относительному пути media/..."""
    url = media_absolute_url(relative_path)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.content


def resolve_local_slug(api_slug: str | None, aliases: dict[str, str]) -> str | None:
    if not api_slug:
        return None
    return aliases.get(api_slug, api_slug)


def image_filename(relative_url: str) -> str:
    return os.path.basename((relative_url or "image.jpg").split("?")[0]) or "image.jpg"
