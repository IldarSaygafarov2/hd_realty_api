from ninja import Router, Query

from project.apps.advertisements.models import Advertisement
from project.apps.advertisements.schemas import (
    AdvertisementCharacteristicSchema,
    AdvertisementCreatorSchema,
    AdvertisementDetailSchema,
    AdvertisementListSchema,
    PaginatedAdvertisementsSchema,
)

router = Router(tags=["advertisements"])

# Базовый queryset для публичного API: одобрены модерацией и активны
def _public_queryset(select_creator: bool = True):
    qs = Advertisement.objects.filter(
        moderation_status=Advertisement.ModerationStatus.APPROVED,
        status=Advertisement.Status.ACTIVE,
    ).select_related("category", "district")
    if select_creator:
        qs = qs.select_related("created_by")
    return qs


def _build_media_url(request, field) -> str | None:
    """Собрать полный URL для медиа-файла."""
    if not field:
        return None
    url = field.url
    if request and hasattr(request, "build_absolute_uri"):
        return request.build_absolute_uri(url)
    return url


def _to_creator_schema(user) -> AdvertisementCreatorSchema | None:
    if not user:
        return None
    phone = getattr(user, "phone", None)
    if phone is not None and not isinstance(phone, str):
        phone = str(phone)
    return AdvertisementCreatorSchema(
        username=user.get_username(),
        phone=phone,
    )


def _to_list_schema(request, ad: Advertisement) -> AdvertisementListSchema:
    return AdvertisementListSchema(
        id=ad.id,
        title=ad.title,
        slug=ad.slug,
        cover_image_url=_build_media_url(request, ad.cover_image),
        price=ad.price,
        currency=ad.currency,
        num_rooms=ad.num_rooms,
        address=ad.address or "",
        district_name=ad.district.name,
        category_name=ad.category.name,
        is_hot=ad.is_hot,
        creator=_to_creator_schema(ad.created_by),
        created_at=ad.created_at.isoformat() if ad.created_at else "",
    )


def _to_detail_schema(request, ad: Advertisement) -> AdvertisementDetailSchema:
    ad.refresh_from_db()  # на случай select_related
    images = list(ad.images.all().order_by("id"))
    return AdvertisementDetailSchema(
        id=ad.id,
        title=ad.title,
        slug=ad.slug,
        description=ad.description or "",
        cover_image_url=_build_media_url(request, ad.cover_image),
        video_url=_build_media_url(request, ad.video) if ad.video else None,
        price=ad.price,
        currency=ad.currency,
        status=ad.status,
        moderation_status=ad.moderation_status,
        num_rooms=ad.num_rooms,
        area_total=ad.area_total,
        area_living=ad.area_living,
        floor_number=ad.floor_number,
        total_floors=ad.total_floors,
        ceiling_height=ad.ceiling_height,
        year_built=ad.year_built,
        renovation_type=ad.renovation_type or "",
        address=ad.address or "",
        latitude=ad.latitude,
        longitude=ad.longitude,
        district_id=ad.district_id,
        district_name=ad.district.name,
        category_id=ad.category_id,
        category_name=ad.category.name,
        image_urls=[
            _build_media_url(request, img.image) or ""
            for img in images
            if img.image
        ],
        characteristics=[
            AdvertisementCharacteristicSchema(name=c.name, value=c.value)
            for c in ad.characteristics.all().order_by("id")
        ],
        views_count=ad.views_count,
        created_at=ad.created_at.isoformat() if ad.created_at else "",
    )


@router.get(
    "/advertisements",
    response=PaginatedAdvertisementsSchema,
)
def list_advertisements(
    request,
    limit: int = Query(20, ge=1, le=100, description="Количество на странице"),
    offset: int = Query(0, ge=0, description="Смещение"),
    is_hot: bool | None = Query(
        None, description="Только горячие объявления (is_hot=True)"
    ),
):
    """
    Список объявлений с пагинацией.
    Параметры: limit (1-100), offset, is_hot (опционально — только горячие).
    """
    qs = _public_queryset().order_by("-created_at")
    if is_hot is True:
        qs = qs.filter(is_hot=True)
    total = qs.count()
    items = qs[offset : offset + limit]
    return PaginatedAdvertisementsSchema(
        items=[_to_list_schema(request, ad) for ad in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/advertisements/{slug}", response={200: AdvertisementDetailSchema, 404: dict})
def get_advertisement(request, slug: str):
    """Детальная информация об объявлении по slug."""
    try:
        ad = _public_queryset().prefetch_related(
            "images", "characteristics"
        ).get(slug=slug)
    except Advertisement.DoesNotExist:
        return 404, {"detail": "Not found"}
    ad.views_count += 1
    ad.save(update_fields=["views_count"])
    return _to_detail_schema(request, ad)
