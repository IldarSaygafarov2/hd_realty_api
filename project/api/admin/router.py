"""
API для админ-панели (session auth).
"""
from ninja import Router

from project.apps.users.models import Notification

router = Router(tags=["admin"])


@router.get(
    "/admin/notifications/unread",
    response={200: dict, 401: dict},
)
def get_unread_notifications(request):
    """
    Список непрочитанных уведомлений текущего пользователя.
    Требует авторизации в админке (session).
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return 401, {"detail": "Authentication required"}
    qs = Notification.objects.filter(user=request.user, is_read=False)
    count = qs.count()
    notifications = list(qs.order_by("-created_at")[:20].values(
        "id", "title", "message", "created_at"
    ))
    items = [
        {
            **n,
            "created_at": n["created_at"].isoformat() if n["created_at"] else "",
        }
        for n in notifications
    ]
    return {"count": count, "items": items}
