from modeltranslation.translator import TranslationOptions, register

from .models import Category


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)
    required_languages = ("ru", "uz")
