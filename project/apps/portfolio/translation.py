from modeltranslation.translator import TranslationOptions, register

from .models import PortfolioCompletedWork, PortfolioItem, PortfolioItemImage


@register(PortfolioItem)
class PortfolioItemTranslationOptions(TranslationOptions):
    fields = ("title", "description")
    required_languages = ("ru", "uz")


@register(PortfolioItemImage)
class PortfolioItemImageTranslationOptions(TranslationOptions):
    fields = ()  # нет переводимых полей, регистрация для совместимости с inlines


@register(PortfolioCompletedWork)
class PortfolioCompletedWorkTranslationOptions(TranslationOptions):
    fields = ("title",)
    required_languages = ("ru", "uz")
