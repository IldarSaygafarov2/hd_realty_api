from decimal import Decimal

from ninja import Router, Query

from project.apps.advertisements.models import Advertisement, RenovationType
from project.apps.advertisements.schemas import (
    AdvertisementCategoryNestedSchema,
    AdvertisementCharacteristicSchema,
    AdvertisementCreatorSchema,
    AdvertisementDetailSchema,
    AdvertisementDistrictNestedSchema,
    AdvertisementListSchema,
    PaginatedAdvertisementsSchema,
    RenovationTypeSchema,
)

router = Router(tags=["advertisements"])

# Значения query для «Любой» в выпадающем списке рынка (новостройка / вторичка / любой)
_HOUSING_MARKET_SKIP_VALUES = frozenset(
    {"any", "all", "*", "любой", "lyuboy"},
)


def _housing_market_query_applies(raw: str | None) -> bool:
    if raw is None:
        return False
    s = raw.strip().lower()
    return bool(s) and s not in _HOUSING_MARKET_SKIP_VALUES


def _parse_comma_separated_slugs(value: str | None) -> list[str]:
    if not value or not value.strip():
        return []
    return [p.strip() for p in value.split(",") if p.strip()]


# Базовый queryset для публичного API: одобрены модерацией и активны
def _public_queryset(select_creator: bool = True):
    qs = Advertisement.objects.filter(
        moderation_status=Advertisement.ModerationStatus.APPROVED,
        status=Advertisement.Status.ACTIVE,
    ).select_related("category", "district", "renovation_type")
    if select_creator:
        qs = qs.select_related(
            "created_by",
            "created_by__profile",
            "created_by__realtor_profile",
        )
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
    profile = getattr(user, "profile", None)
    phone = getattr(profile, "phone", None) if profile is not None else None
    if phone is not None and not isinstance(phone, str):
        phone = str(phone)
    if not phone:
        phone = None
    first_name = getattr(user, "first_name", "") or ""
    last_name = getattr(user, "last_name", "") or ""
    full_name = ""
    get_full_name = getattr(user, "get_full_name", None)
    if callable(get_full_name):
        full_name = (get_full_name() or "").strip()
    if not full_name:
        full_name = " ".join(p for p in (first_name, last_name) if p).strip()
    email = getattr(user, "email", "") or None
    seller_type = "user"
    try:
        user.realtor_profile  # noqa: B018
    except AttributeError:
        pass
    else:
        seller_type = "realtor"
    return AdvertisementCreatorSchema(
        username=user.get_username(),
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        email=email,
        phone=phone,
        seller_type=seller_type,
    )


def _to_renovation_type_schema(rt) -> RenovationTypeSchema | None:
    if rt is None:
        return None
    return RenovationTypeSchema(
        id=rt.id,
        slug=rt.slug,
        name=rt.name,
        name_ru=getattr(rt, "name_ru", None),
        name_uz=getattr(rt, "name_uz", None),
    )


def _to_list_schema(request, ad: Advertisement) -> AdvertisementListSchema:
    cat = ad.category
    dist = ad.district
    images = sorted(ad.images.all(), key=lambda img: img.id)
    image_urls = [
        url
        for url in (_build_media_url(request, img.image) for img in images if img.image)
        if url
    ]
    return AdvertisementListSchema(
        id=ad.id,
        title=ad.title,
        slug=ad.slug,
        description=ad.description or "",
        cover_image_url=_build_media_url(request, ad.cover_image),
        image_urls=image_urls,
        price=ad.price,
        price_usd=ad.price_usd,
        currency=ad.currency,
        deal_type=ad.deal_type,
        housing_market=ad.housing_market,
        residential_complex_name=ad.residential_complex_name or "",
        developer=ad.developer or "",
        num_rooms=ad.num_rooms,
        area_total=ad.area_total,
        area_living=ad.area_living,
        floor_number=ad.floor_number,
        total_floors=ad.total_floors,
        ceiling_height=ad.ceiling_height,
        renovation_type=_to_renovation_type_schema(ad.renovation_type),
        parking_type=ad.parking_type or "",
        housing_class=ad.housing_class or "",
        finishing_type=ad.finishing_type or "",
        is_furnished=ad.is_furnished,
        has_commission=ad.has_commission,
        address=ad.address or "",
        landmark=ad.landmark or "",
        street_intersection=ad.street_intersection or "",
        category=AdvertisementCategoryNestedSchema(
            id=cat.id,
            slug=cat.slug,
            name=cat.name,
            name_ru=cat.name_ru,
            name_uz=cat.name_uz,
        ),
        district=AdvertisementDistrictNestedSchema(
            id=dist.id,
            slug=dist.slug,
            name=dist.name,
            name_ru=dist.name_ru,
            name_uz=dist.name_uz,
        ),
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
        price_usd=ad.price_usd,
        currency=ad.currency,
        deal_type=ad.deal_type,
        housing_market=ad.housing_market,
        residential_complex_name=ad.residential_complex_name or "",
        developer=ad.developer or "",
        status=ad.status,
        moderation_status=ad.moderation_status,
        num_rooms=ad.num_rooms,
        area_total=ad.area_total,
        area_living=ad.area_living,
        floor_number=ad.floor_number,
        total_floors=ad.total_floors,
        ceiling_height=ad.ceiling_height,
        year_built=ad.year_built,
        renovation_type=_to_renovation_type_schema(ad.renovation_type),
        parking_type=ad.parking_type or "",
        housing_class=ad.housing_class or "",
        finishing_type=ad.finishing_type or "",
        is_furnished=ad.is_furnished,
        has_commission=ad.has_commission,
        address=ad.address or "",
        landmark=ad.landmark or "",
        street_intersection=ad.street_intersection or "",
        latitude=ad.latitude,
        longitude=ad.longitude,
        district_id=ad.district_id,
        district_name=ad.district.name,
        category_id=ad.category_id,
        category_name=ad.category.name,
        image_urls=[
            _build_media_url(request, img.image) or "" for img in images if img.image
        ],
        characteristics=[
            AdvertisementCharacteristicSchema(name=c.name, value=c.value)
            for c in ad.characteristics.all().order_by("id")
        ],
        creator=_to_creator_schema(ad.created_by),
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
    if deal_type is not None and str(deal_type).strip():
        dt = str(deal_type).strip().lower()
        if dt not in dt_values:
            return qs.none()
        qs = qs.filter(deal_type=dt)
    if _housing_market_query_applies(housing_market):
        hm = str(housing_market).strip().lower()
        if hm not in hm_values:
            return qs.none()
        qs = qs.filter(housing_market=hm)
    category_slugs = _parse_comma_separated_slugs(
        str(category_slug).strip() if category_slug else None
    )
    if category_slugs:
        qs = qs.filter(category__slug__in=category_slugs)
    district_slugs = _parse_comma_separated_slugs(
        str(district_slug).strip() if district_slug else None
    )
    if district_slugs:
        qs = qs.filter(district__slug__in=district_slugs)
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
        description=(
            "Рынок жилья (как в UI): new_building, secondary. "
            "Любой вариант — не передавать параметр или передать any / любой"
        ),
    ),
    category_slug: str | None = Query(
        None,
        description="Slug категории; несколько через запятую, например kvartira,dom",
    ),
    district_slug: str | None = Query(
        None,
        description="Slug района; несколько через запятую, например yunusobod,chilonzor",
    ),
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
    qs = _public_queryset().prefetch_related("images").order_by("-created_at")
    if is_hot is True:
        qs = qs.filter(is_hot=True)
    qs = _apply_list_filters(
        qs,
        deal_type=deal_type.strip() if deal_type else None,
        housing_market=housing_market.strip() if housing_market else None,
        category_slug=category_slug.strip() if category_slug else None,
        district_slug=district_slug.strip() if district_slug else None,
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


@router.get(
    "/advertisements/{slug}", response={200: AdvertisementDetailSchema, 404: dict}
)
def get_advertisement(request, slug: str):
    """Детальная информация об объявлении по slug."""
    try:
        ad = (
            _public_queryset()
            .prefetch_related("images", "characteristics")
            .get(slug=slug)
        )
    except Advertisement.DoesNotExist:
        return 404, {"detail": "Not found"}
    ad.views_count += 1
    ad.save(update_fields=["views_count"])
    return _to_detail_schema(request, ad)


@router.get(
    "/renovation-types", response=list[RenovationTypeSchema], tags=["renovation-types"]
)
def list_renovation_types(request):
    """Список всех типов ремонта."""
    return [_to_renovation_type_schema(rt) for rt in RenovationType.objects.all()]
