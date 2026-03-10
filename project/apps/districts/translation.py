from modeltranslation.translator import TranslationOptions, register

from .models import District


@register(District)
class DistrictTranslationOptions(TranslationOptions):
    fields = ("name",)
    required_languages = ("ru", "uz")
