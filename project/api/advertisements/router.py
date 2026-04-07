from decimal import Decimal

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
        deal_type=ad.deal_type,
        housing_market=ad.housing_market,
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
        deal_type=ad.deal_type,
        housing_market=ad.housing_market,
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


def _apply_list_filters(
    qs,
    *,
    deal_type: str | None,
    housing_market: str | None,
    category_slug: str | None,
    district_slug: str | None,
    rooms: int | None,
    price_min: Decimal | None,
    price_max: Decimal | None,
):
    dt_values = {c[0] for c in Advertisement.DealType.choices}
    hm_values = {c[0] for c in Advertisement.HousingMarket.choices}
    if deal_type is not None:
        if deal_type not in dt_values:
            return qs.none()
        qs = qs.filter(deal_type=deal_type)
    if housing_market is not None:
        if housing_market not in hm_values:
            return qs.none()
        qs = qs.filter(housing_market=housing_market)
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if district_slug:
        qs = qs.filter(district__slug=district_slug)
    if rooms is not None:
        if rooms not in (0, 1, 2, 3, 4):
            return qs.none()
        if rooms == 4:
            qs = qs.filter(num_rooms__gte=4)
        else:
            qs = qs.filter(num_rooms=rooms)
    if price_min is not None:
        qs = qs.filter(price__gte=price_min)
    if price_max is not None:
        qs = qs.filter(price__lte=price_max)
    return qs


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
    deal_type: str | None = Query(
        None,
        description="Тип сделки: rent (аренда), sale (покупка)",
    ),
    housing_market: str | None = Query(
        None,
        description="Рынок: new_building (новостройка), secondary (вторичка)",
    ),
    category_slug: str | None = Query(
        None, description="Slug категории (тип недвижимости), например kvartira"
    ),
    district_slug: str | None = Query(None, description="Slug района"),
    rooms: int | None = Query(
        None,
        ge=0,
        le=4,
        description="Комнаты: 0=студия, 1–3 точно, 4=четыре и больше",
    ),
    price_min: Decimal | None = Query(None, ge=0, description="Цена от"),
    price_max: Decimal | None = Query(None, ge=0, description="Цена до"),
):
    """
    Список объявлений с пагинацией и фильтрами (как на экране поиска).
    """
    qs = _public_queryset().order_by("-created_at")
    if is_hot is True:
        qs = qs.filter(is_hot=True)
    qs = _apply_list_filters(
        qs,
        deal_type=deal_type,
        housing_market=housing_market,
        category_slug=category_slug or None,
        district_slug=district_slug or None,
        rooms=rooms,
        price_min=price_min,
        price_max=price_max,
    )
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
