"""
Сервис для работы с районами.
"""
from project.apps.districts.models import District


class DistrictService:
    """Сервис районов."""

    @staticmethod
    def list_districts():
        """Получить список всех районов."""
        return list(District.objects.all())

    @staticmethod
    def get_by_slug(slug: str) -> District | None:
        """Получить район по slug."""
        try:
            return District.objects.get(slug=slug)
        except District.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(pk: int) -> District | None:
        """Получить район по id."""
        try:
            return District.objects.get(pk=pk)
        except District.DoesNotExist:
            return None

    @staticmethod
    def create(name_ru: str, name_uz: str, slug: str) -> District:
        """Создать район."""
        return District.objects.create(name=name_ru, name_uz=name_uz, slug=slug)

    @staticmethod
    def update(
        district: District,
        *,
        name_ru: str | None = None,
        name_uz: str | None = None,
        slug: str | None = None,
    ) -> District:
        """Обновить район."""
        if name_ru is not None:
            district.name = name_ru
        if name_uz is not None:
            district.name_uz = name_uz
        if slug is not None:
            district.slug = slug
        district.save(update_fields=["name", "name_uz", "slug", "updated_at"])
        return district

    @staticmethod
    def delete(district: District) -> None:
        """Удалить район."""
        district.delete()
