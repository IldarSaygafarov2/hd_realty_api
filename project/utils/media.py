"""Пути к медиа-файлам для ответов API (без домена и протокола)."""

from __future__ import annotations

from urllib.parse import urlparse


def media_file_path(field) -> str | None:
    """Относительный путь к файлу, например `/media/advertisements/...`."""
    if not field:
        return None
    url = (field.url or "").strip()
    if not url:
        return None
    if url.startswith(("http://", "https://")):
        path = urlparse(url).path
        return path or None
    if not url.startswith("/"):
        return f"/{url}"
    return url
