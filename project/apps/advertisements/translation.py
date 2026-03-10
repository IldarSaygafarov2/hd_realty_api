from modeltranslation.translator import TranslationOptions, register

from .models import Advertisement, AdvertisementCharacteristic, AdvertisementImage


@register(AdvertisementImage)
class AdvertisementImageTranslationOptions(TranslationOptions):
    fields = ()  # нет переводимых полей, регистрация для совместимости с inlines


@register(Advertisement)
class AdvertisementTranslationOptions(TranslationOptions):
    fields = ("title", "description", "address")
    required_languages = ("ru", "uz")


@register(AdvertisementCharacteristic)
class AdvertisementCharacteristicTranslationOptions(TranslationOptions):
    fields = ("name", "value")
    required_languages = ("ru", "uz")
