from ninja import Schema


class CategorySchema(Schema):
    """Схема категории (name зависит от Accept-Language)."""

    id: int
    name: str
    slug: str


class CategoryCreateSchema(Schema):
    """Схема создания категории."""

    name_ru: str
    name_uz: str
    slug: str


class CategoryUpdateSchema(Schema):
    """Схема обновления категории."""

    name_ru: str | None = None
    name_uz: str | None = None
    slug: str | None = None
