"""Утилиты для проверки ролей."""


def is_realtor(user):
    """Пользователь — риелтор."""
    return hasattr(user, "realtor_profile") and user.realtor_profile is not None


def is_moderator(user):
    """Пользователь — модератор."""
    return hasattr(user, "moderator_profile") and user.moderator_profile is not None


def get_realtor(user):
    """Профиль риелтора или None."""
    return getattr(user, "realtor_profile", None)


def get_moderator(user):
    """Профиль модератора или None."""
    return getattr(user, "moderator_profile", None)
