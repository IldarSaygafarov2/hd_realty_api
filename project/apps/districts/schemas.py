from ninja import Schema


class DistrictSchema(Schema):
    """Схема района (name зависит от Accept-Language)."""

    id: int
    name: str
    slug: str


class DistrictCreateSchema(Schema):
    """Схема создания района."""

    name_ru: str
    name_uz: str
    slug: str


class DistrictUpdateSchema(Schema):
    """Схема обновления района."""

    name_ru: str | None = None
    name_uz: str | None = None
    slug: str | None = None
