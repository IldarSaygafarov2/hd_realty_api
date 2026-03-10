from ninja import Router

from project.apps.categories.schemas import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)
from project.application.categories.service import CategoryService

router = Router(tags=["categories"])


def _to_schema(category) -> CategorySchema:
    return CategorySchema(id=category.id, name=category.name, slug=category.slug)


@router.get("/categories", response=list[CategorySchema])
def list_categories(request):
    """Список категорий."""
    categories = CategoryService.list_categories()
    return [_to_schema(c) for c in categories]


@router.get("/categories/{slug}", response={200: CategorySchema, 404: dict})
def get_category(request, slug: str):
    """Категория по slug."""
    category = CategoryService.get_by_slug(slug)
    if category is None:
        return 404, {"detail": "Not found"}
    return _to_schema(category)


@router.post("/categories", response={201: CategorySchema})
def create_category(request, payload: CategoryCreateSchema):
    """Создать категорию."""
    category = CategoryService.create(
        name_ru=payload.name_ru,
        name_uz=payload.name_uz,
        slug=payload.slug,
    )
    return 201, _to_schema(category)


@router.put("/categories/{slug}", response={200: CategorySchema, 404: dict})
def update_category(request, slug: str, payload: CategoryUpdateSchema):
    """Обновить категорию."""
    category = CategoryService.get_by_slug(slug)
    if category is None:
        return 404, {"detail": "Not found"}
    updated = CategoryService.update(
        category,
        name_ru=payload.name_ru,
        name_uz=payload.name_uz,
        slug=payload.slug,
    )
    return _to_schema(updated)


@router.delete("/categories/{slug}", response={204: None, 404: dict})
def delete_category(request, slug: str):
    """Удалить категорию."""
    category = CategoryService.get_by_slug(slug)
    if category is None:
        return 404, {"detail": "Not found"}
    CategoryService.delete(category)
    return 204, None
