from ninja import Router

from project.apps.districts.schemas import (
    DistrictCreateSchema,
    DistrictSchema,
    DistrictUpdateSchema,
)
from project.application.districts.service import DistrictService

router = Router(tags=["districts"])


def _to_schema(district) -> DistrictSchema:
    return DistrictSchema(id=district.id, name=district.name, slug=district.slug)


@router.get("/districts", response=list[DistrictSchema])
def list_districts(request):
    """Список районов."""
    districts = DistrictService.list_districts()
    return [_to_schema(d) for d in districts]


@router.get("/districts/{slug}", response={200: DistrictSchema, 404: dict})
def get_district(request, slug: str):
    """Район по slug (ru или uz)."""
    district = DistrictService.get_by_slug(slug)
    if district is None:
        return 404, {"detail": "Not found"}
    return _to_schema(district)


@router.post("/districts", response={201: DistrictSchema})
def create_district(request, payload: DistrictCreateSchema):
    """Создать район."""
    district = DistrictService.create(
        name_ru=payload.name_ru,
        name_uz=payload.name_uz,
        slug=payload.slug,
    )
    return 201, _to_schema(district)


@router.put("/districts/{slug}", response={200: DistrictSchema, 404: dict})
def update_district(request, slug: str, payload: DistrictUpdateSchema):
    """Обновить район."""
    district = DistrictService.get_by_slug(slug)
    if district is None:
        return 404, {"detail": "Not found"}
    updated = DistrictService.update(
        district,
        name_ru=payload.name_ru,
        name_uz=payload.name_uz,
        slug=payload.slug,
    )
    return _to_schema(updated)


@router.delete("/districts/{slug}", response={204: None, 404: dict})
def delete_district(request, slug: str):
    """Удалить район."""
    district = DistrictService.get_by_slug(slug)
    if district is None:
        return 404, {"detail": "Not found"}
    DistrictService.delete(district)
    return 204, None
