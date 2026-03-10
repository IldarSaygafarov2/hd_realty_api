"""
API routers - подключайте сюда роутеры для модулей.
"""
from ninja import Router

router = Router(tags=["common"])


@router.get("/ping")
def ping(request):
    """Health check для API."""
    return {"pong": True}
