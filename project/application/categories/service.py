"""
Сервис для работы с категориями.
"""
from project.apps.categories.models import Category


class CategoryService:
    """Сервис категорий."""

    @staticmethod
    def list_categories():
        """Получить список всех категорий."""
        return list(Category.objects.all())

    @staticmethod
    def get_by_slug(slug: str) -> Category | None:
        """Получить категорию по slug."""
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(pk: int) -> Category | None:
        """Получить категорию по id."""
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    @staticmethod
    def create(name_ru: str, name_uz: str, slug: str) -> Category:
        """Создать категорию."""
        return Category.objects.create(name=name_ru, name_uz=name_uz, slug=slug)

    @staticmethod
    def update(
        category: Category,
        *,
        name_ru: str | None = None,
        name_uz: str | None = None,
        slug: str | None = None,
    ) -> Category:
        """Обновить категорию."""
        if name_ru is not None:
            category.name = name_ru
        if name_uz is not None:
            category.name_uz = name_uz
        if slug is not None:
            category.slug = slug
        category.save(update_fields=["name", "name_uz", "slug", "updated_at"])
        return category

    @staticmethod
    def delete(category: Category) -> None:
        """Удалить категорию."""
        category.delete()
