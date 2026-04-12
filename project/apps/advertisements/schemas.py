from decimal import Decimal

from ninja import Schema


class AdvertisementCreatorSchema(Schema):
    """Создатель объявления (пользователь)."""

    username: str
    phone: str | None = None
    # user — обычный пользователь; realtor — есть профиль риелтора
    seller_type: str


class AdvertisementCategoryNestedSchema(Schema):
    """Категория в списке объявлений (полные данные с переводами)."""

    id: int
    slug: str
    name: str
    name_ru: str | None = None
    name_uz: str | None = None


class AdvertisementDistrictNestedSchema(Schema):
    """Район в списке объявлений (полные данные с переводами)."""

    id: int
    slug: str
    name: str
    name_ru: str | None = None
    name_uz: str | None = None


class AdvertisementListSchema(Schema):
    """Схема объявления для списка (карточка на витрине)."""

    id: int
    title: str
    slug: str
    description: str
    cover_image_url: str | None
    price: Decimal
    currency: str
    deal_type: str
    housing_market: str
    residential_complex_name: str
    developer: str
    num_rooms: int
    area_total: Decimal | None
    area_living: Decimal | None
    floor_number: int | None
    total_floors: int | None
    ceiling_height: Decimal | None
    renovation_type: str
    parking_type: str
    housing_class: str
    finishing_type: str
    is_furnished: bool | None
    has_commission: bool
    address: str
    landmark: str
    street_intersection: str
    category: AdvertisementCategoryNestedSchema
    district: AdvertisementDistrictNestedSchema
    is_hot: bool
    creator: AdvertisementCreatorSchema | None = None
    created_at: str


class PaginatedAdvertisementsSchema(Schema):
    """Пагинированный список объявлений."""

    items: list[AdvertisementListSchema]
    total: int
    limit: int
    offset: int


class AdvertisementCharacteristicSchema(Schema):
    """Характеристика объявления."""

    name: str
    value: str


class AdvertisementDetailSchema(Schema):
    """Схема объявления для детальной страницы."""

    id: int
    title: str
    slug: str
    description: str
    cover_image_url: str | None
    video_url: str | None
    price: Decimal
    currency: str
    deal_type: str
    housing_market: str
    residential_complex_name: str
    developer: str
    status: int
    moderation_status: int
    num_rooms: int
    area_total: Decimal | None
    area_living: Decimal | None
    floor_number: int | None
    total_floors: int | None
    ceiling_height: Decimal | None
    year_built: int | None
    renovation_type: str
    parking_type: str
    housing_class: str
    finishing_type: str
    is_furnished: bool | None
    has_commission: bool
    address: str
    landmark: str
    street_intersection: str
    latitude: Decimal | None
    longitude: Decimal | None
    district_id: int
    district_name: str
    category_id: int
    category_name: str
    image_urls: list[str]
    characteristics: list[AdvertisementCharacteristicSchema]
    views_count: int
    created_at: str
