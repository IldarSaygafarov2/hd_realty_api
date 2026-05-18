"""Утилита для отладки внешнего API импорта (python -m project.utils.parser)."""

from pprint import pprint

from project.utils.listing_import import (
    OPERATION_TYPES,
    fetch_advertisement_detail,
    iter_advertisements,
)


def main() -> None:
    for operation_type in OPERATION_TYPES:
        for advertisement in iter_advertisements(operation_type, limit=2, max_pages=1):
            detail = fetch_advertisement_detail(advertisement["id"])
            pprint(detail)
            return


if __name__ == "__main__":
    main()
