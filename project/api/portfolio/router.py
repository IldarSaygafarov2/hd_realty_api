from ninja import Router

from project.apps.portfolio.models import PortfolioItem
from project.apps.portfolio.schemas import (
    PortfolioCompletedWorkSchema,
    PortfolioItemDetailSchema,
    PortfolioItemListSchema,
)

router = Router(tags=["portfolio"])


def _build_media_url(request, field) -> str | None:
    if not field:
        return None
    url = field.url
    if request and hasattr(request, "build_absolute_uri"):
        return request.build_absolute_uri(url)
    return url


def _to_completed_works(item: PortfolioItem) -> list[PortfolioCompletedWorkSchema]:
    return [
        PortfolioCompletedWorkSchema(
            id=w.id,
            title=w.title,
            title_ru=w.title_ru,
            title_uz=w.title_uz,
            icon=w.icon or "",
        )
        for w in item.completed_works.all()
    ]


def _to_list_schema(request, item: PortfolioItem) -> PortfolioItemListSchema:
    return PortfolioItemListSchema(
        id=item.id,
        title=item.title,
        title_ru=item.title_ru,
        title_uz=item.title_uz,
        description=item.description or "",
        video_url=_build_media_url(request, item.video),
        image_urls=[
            _build_media_url(request, img.image) or ""
            for img in item.images.all()
            if img.image
        ],
        completed_works=_to_completed_works(item),
        created_at=item.created_at.isoformat() if item.created_at else "",
    )


def _to_detail_schema(request, item: PortfolioItem) -> PortfolioItemDetailSchema:
    return PortfolioItemDetailSchema(
        id=item.id,
        title=item.title,
        title_ru=item.title_ru,
        title_uz=item.title_uz,
        description=item.description or "",
        description_ru=item.description_ru,
        description_uz=item.description_uz,
        video_url=_build_media_url(request, item.video),
        image_urls=[
            _build_media_url(request, img.image) or ""
            for img in item.images.all()
            if img.image
        ],
        completed_works=_to_completed_works(item),
        created_at=item.created_at.isoformat() if item.created_at else "",
    )


def _active_queryset():
    return (
        PortfolioItem.objects.filter(is_active=True)
        .prefetch_related("images", "completed_works")
        .order_by("-created_at")
    )


@router.get("/portfolio", response=list[PortfolioItemListSchema])
def list_portfolio(request):
    """Список примеров работ (только активные)."""
    items = _active_queryset()
    return [_to_list_schema(request, item) for item in items]


@router.get("/portfolio/{item_id}", response={200: PortfolioItemDetailSchema, 404: dict})
def get_portfolio_item(request, item_id: int):
    """Пример работы по ID."""
    try:
        item = _active_queryset().get(id=item_id)
    except PortfolioItem.DoesNotExist:
        return 404, {"detail": "Not found"}
    return _to_detail_schema(request, item)
