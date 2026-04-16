from ninja import Schema


class PortfolioCompletedWorkSchema(Schema):
    """Выполненная работа (тег «Было выполнено»)."""

    id: int
    title: str
    title_ru: str | None = None
    title_uz: str | None = None
    icon: str


class PortfolioItemListSchema(Schema):
    """Пример работы для списка."""

    id: int
    title: str
    title_ru: str | None = None
    title_uz: str | None = None
    description: str
    video_url: str | None = None
    image_urls: list[str]
    completed_works: list[PortfolioCompletedWorkSchema]
    created_at: str


class PortfolioItemDetailSchema(PortfolioItemListSchema):
    """Пример работы — детальная страница (расширяет список)."""

    description_ru: str | None = None
    description_uz: str | None = None
