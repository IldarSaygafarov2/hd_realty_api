from django.apps import AppConfig


class AdvertisementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "project.apps.advertisements"
    verbose_name = "Объявления"

    def ready(self) -> None:
        # Регистрируем обработчик сигнала об изменении настроек constance
        # (в т.ч. USD_RATE через админку) — он перезапустит пересчёт цен.
        from project.apps.advertisements import signals  # noqa: F401
